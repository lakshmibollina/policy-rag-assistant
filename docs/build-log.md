# Build log

One entry per step: what was done, the decisions made and why, problems hit, and measured results.

## Step 1: Setup (2026-10-01)

- **Did:** created the repo, folder structure (`src`, `data`, `evals`, `prompts`, `docs`), `requirements.txt`, `.env.example` and README.
- **Decided:** one repo per project; secrets live in `.env`, which is git-ignored; dependencies listed in `requirements.txt`.
- **Why:** anyone can clone and run it, and no API key ever reaches GitHub.

## Step 2: Data and real questions (2026-10-05)

- **Did:** chose public health plan Summary of Benefits and Coverage (SBC) PDFs as the documents, listed them in `data/sources.csv` with a download script, and wrote 10 real customer questions.
- **Decided:** keep the PDFs out of Git and record their sources instead.
- **Why:** the PDFs belong to the insurers and get updated each year; a source list plus a script keeps the repo small and makes the dataset reproducible.
- **Decided:** included a question the documents should *not* answer positively (cosmetic surgery) so I can test that the assistant says "not covered" or "not found" instead of making something up.
- **Problems hit:** `nj-shbp-sbc059.pdf` returns HTTP 404 (checked 2026-10-06), so 6 of 7 PDFs download. Replaced it with SBC 218 (NJ DIRECT 2030 PPO) from the same program; all 7 now download.

## Step 3: Ingest documents into a vector database (2026-10-06)

- **Did:** wrote `src/ingest.py`. It reads each PDF page by page with pypdf, splits each page into ~600-token chunks with 100-token overlap, tags every chunk with its file name and page number, embeds the chunks with sentence-transformers, and stores them in a local ChromaDB collection (`chroma_db/`, collection `policies`, cosine distance).
- **Decided:** chunk within a page, never across pages. **Why:** every chunk then has exactly one page number to cite. SBC pages are short (most produce 1 or 2 chunks), so little context is lost.
- **Decided:** measure chunk size with the embedding model's own tokenizer, and use `nomic-ai/modernbert-embed-base` (8192-token window). **Why:** popular small models such as `all-MiniLM-L6-v2` only read 256 tokens and silently drop the rest of a 600-token chunk. This model needs `search_document: ` / `search_query: ` prefixes, which are defined in `ingest.py` for step 4 to use.
- **Decided:** each run deletes and rebuilds the collection. **Why:** re-running never leaves duplicate or stale chunks; with ~90 chunks a full rebuild is cheap.
- **Result:** 7 PDFs, 58 pages, 102 chunks. Chunk size min 40 / median 485 / max 598 tokens. Embedding took ~1.7 minutes on CPU.

## Step 4: Answer with citations (2026-10-06)

- **Did:** wrote `src/answer.py`. It embeds the question with the same model and `search_query: ` prefix as ingestion, retrieves the top 5 chunks from ChromaDB, and sends them to llama3.2 through Ollama with the prompt in `prompts/answer_v1.txt`. Usage: `python src/answer.py "question"`; it prints the answer and the time taken.
- **Decided:** llama3.2 (3B) running locally through Ollama, temperature 0. **Why:** free, no API key, no data leaves the machine, and temperature 0 makes answers repeatable for evaluation.
- **Decided:** each chunk is labelled in the prompt with its exact citation `[file_name, p.page]`, so the model only has to copy it.
- **Decided:** set Ollama's context window to 8192 tokens. **Why:** the default is too small for 5 chunks of up to 600 tokens plus the prompt, and Ollama cuts off the overflow without warning.
- **Decided:** removed `langchain-openai` (unused) and added `ollama`.
- **Result (3 seed questions, prompt v1):**

  | Question | Outcome |
  | --- | --- |
  | q01 deductible | Correct figures ($7,500 individual / $15,000 family, BCBS Texas), but the citation misspells the file name (`bcbs-tx-...` instead of `bcbstx-...`). Answered for one plan only. |
  | q02 physical therapy | Wrong. Copied raw excerpts, then replied "Not found", although SC PEBA p.4 lists rehabilitation services at a $15 copay. |
  | q10 cosmetic surgery | **Dangerously wrong.** The source says "Services Your Plan Generally Does NOT Cover"; the model rewrote it as "DOES COVER" and concluded the plans cover cosmetic surgery. |

- **Latency:** 94 to 131 seconds per answer. Ollama runs the model 100% on the CPU (no GPU).
- **Takeaway:** retrieval found the right pages for all three questions; the failures are in generation. A 3B model does not follow the grounding rules reliably. Next: measure this properly on the step 5 test set, and compare a stronger model and a stricter prompt (v2) against it.
