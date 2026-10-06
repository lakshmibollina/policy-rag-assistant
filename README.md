# Policy RAG Assistant: Cited Answers from Health Insurance Documents

Build a retrieval-augmented generation (RAG) system that answers health insurance questions using **only** the plan's own documents, cites the exact document and page for every answer, and says "not found" instead of guessing.

![Status](https://img.shields.io/badge/status-in%20progress%20%E2%80%94%20step%204%20of%209-yellow?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-vector_store-FF6F00?style=flat-square)

## Key Results

Results are measured on a fixed evaluation set and filled in as each stage is completed.

| Metric | Baseline (vector search only) | Final (hybrid + re-ranking) |
| --- | --- | --- |
| Retrieval hit rate @5 (correct page in top 5) | Pending (step 5) | Pending (step 6) |
| Citation accuracy (cited page supports the answer) | Pending (step 5) | Pending (step 6) |
| Faithfulness (answer uses only retrieved text) | Pending (step 5) | Pending (step 6) |
| Correct "not found" on unanswerable questions | Pending (step 5) | Pending (step 6) |
| P95 latency per question | Pending (step 5) | Pending (step 6) |

## Project Overview

Health plan documents are long, dense and full of conditions. A general-purpose chatbot answers coverage questions confidently even when it is wrong, which is unacceptable when money and care decisions depend on the answer. This project builds an assistant that grounds every answer in the source documents, shows its citations so a person can verify them, and is measured against a fixed test set so every change to retrieval or prompts is judged by numbers rather than impressions.

## Methodology

1. **Problem framing:** Started from 10 real customer questions (deductibles, referrals, visit limits, exclusions) rather than from the technology.
2. **Data collection:** Selected 7 public 2026 health plan Summary of Benefits and Coverage (SBC) documents across PPO and HMO plans from 6 issuers. SBCs follow a federally mandated format, so plans can be compared fairly.
3. **Ingestion:** Extract text page by page, split into overlapping chunks, keep document name and page number on every chunk, embed, and store in ChromaDB.
4. **Grounded answering:** Retrieve the top chunks for a question and instruct a local LLM (llama3.2 via Ollama) to answer only from them, cite `[file_name, p.page]`, and reply "Not found in the policy documents" when the answer is absent.
5. **Baseline evaluation:** Build a 50-question test set with expected answers and source pages; score retrieval, citations and faithfulness.
6. **Retrieval improvements:** Add hybrid search (BM25 keyword + vector) and cross-encoder re-ranking; re-score on the same test set.
7. **Interface:** Streamlit app showing the answer with clickable citations.
8. **Regression gating:** GitHub Actions runs the evaluation on every push and fails the build if quality drops.
9. **Failure analysis:** Document remaining failure cases and their causes.

## Repository Structure

```text
├── data/
│   ├── sources.csv              # Document list: issuer, plan, plan type, URL
│   └── raw/                     # Downloaded PDFs (git-ignored)
├── scripts/
│   └── download_data.py         # Downloads and validates the PDFs in sources.csv
├── evals/
│   └── seed_questions.csv       # 10 real customer questions
├── src/                         # Ingestion, retrieval and answering code (step 3+)
├── prompts/                     # Versioned prompt files (step 4+)
├── docs/
│   └── build-log.md             # Decisions, trade-offs and results per step
├── requirements.txt
├── .env.example                 # Required settings, no real values
└── README.md                    # This file
```

## Configuration

Initial choices, to be tuned against the evaluation set.

| Parameter | Value | Justification |
| --- | --- | --- |
| Document format | SBC PDFs | Standard federal format; same sections across plans |
| Chunk size | ~600 tokens | Large enough to hold a full benefit row with its conditions |
| Chunk overlap | 100 tokens | Avoids splitting a limit or exception from its benefit |
| Chunk metadata | Document name, page number | Required for citations |
| Embedding model | `nomic-ai/modernbert-embed-base` via sentence-transformers | Free, runs offline; reads up to 8192 tokens, so a 600-token chunk is embedded in full |
| Vector store | ChromaDB | Simple local persistence; no server to run |
| Top-k retrieved | 5 | Enough context for multi-part answers without diluting the prompt |
| LLM | llama3.2 (3B) via Ollama, temperature 0 | Free and local; deterministic answers so evaluations are repeatable |
| Answer prompt | `prompts/answer_v1.txt` | Versioned so each prompt change can be measured |
| Keyword search | BM25 (step 6) | Catches exact terms such as plan codes and drug tiers |
| Re-ranker | Cross-encoder (step 6) | Reorders candidates by true relevance to the question |

## Data Summary

- 7 Summary of Benefits and Coverage documents, plan year 2026
- 6 issuers: state employee plans (New Jersey, Oklahoma, South Carolina), the Federal Employee Program, Blue Cross Blue Shield of Texas, and Florida Blue
- Mix of PPO and HMO plans
- 10 seed questions, including one designed to test that the assistant reports an exclusion instead of inventing coverage
- 50-question evaluation set with expected answers and source pages (step 5)

## Datasets Used

| Source | Purpose |
| --- | --- |
| Public 2026 SBC documents listed in [`data/sources.csv`](data/sources.csv) | Knowledge base the assistant answers from |
| [`evals/seed_questions.csv`](evals/seed_questions.csv) | Real customer questions that define what the system must handle |

## Tools Used

- **Python**: pipeline, evaluation and scripts
- **pypdf**: page-level PDF text extraction
- **sentence-transformers**: text embeddings
- **ChromaDB**: vector storage and similarity search
- **LangChain text splitters**: token-based chunking
- **Ollama**: runs the llama3.2 LLM locally
- **rank-bm25**: keyword search for hybrid retrieval
- **Streamlit**: demo interface
- **GitHub Actions**: evaluation in CI

## Key Findings

To be written from measured results after evaluation (steps 5 and 6).

## How to Run

```bash
git clone https://github.com/lakshmibollina/policy-rag-assistant.git
cd policy-rag-assistant
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
ollama pull llama3.2               # local LLM, requires Ollama (ollama.com)
python scripts/download_data.py    # downloads the policy PDFs into data/raw/
python src/ingest.py               # chunks, embeds and stores them in chroma_db/
python src/answer.py "Is physical therapy covered?"
```

## Progress

- [x] Step 1: Repo, environment and README
- [x] Step 2: Collect policy documents and real user questions
- [x] Step 3: Ingest documents into a vector database
- [x] Step 4: Answer with citations
- [ ] Step 5: Test set and baseline metrics
- [ ] Step 6: Hybrid search and re-ranking
- [ ] Step 7: Streamlit web app
- [ ] Step 8: CI eval gate
- [ ] Step 9: Failure analysis and final write-up

Decisions and trade-offs for each step are recorded in [docs/build-log.md](docs/build-log.md).

## License

This project is for educational and portfolio purposes. The policy documents belong to their publishers and are not redistributed in this repository.
