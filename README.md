# Policy RAG Assistant

Document Q&A with citations, built like a production system — not a demo.

> **Status:** 🚧 In progress — Step 2 of 9 (collecting documents and real user questions)

**Two flavors:**
- **Health insurance policy assistant** — "Is physiotherapy covered under my plan?" with the exact policy clause cited.
- **HR handbook Q&A bot** — answers from public company employee handbooks.

## How it works

PDFs → chunk → embed → hybrid retrieval (BM25 + vector) → cross-encoder rerank → LLM answer with enforced citations.

## Production features

- Hybrid retrieval (BM25 + vector search)
- Cross-encoder reranking
- Citation enforcement on every answer
- Eval pipeline gated in CI — regressions fail the build

## Results

| Metric | Baseline | Final |
| --- | --- | --- |
| Answer faithfulness | — | — |
| P95 latency | — | — |
| Cost per 1k queries | — | — |

*(Fill in real numbers as you measure them.)*

## Run it

```bash
git clone https://github.com/lakshmibollina/policy-rag-assistant.git
cd policy-rag-assistant
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then add your API key to .env
python scripts/download_data.py    # downloads the policy PDFs into data/raw/
```

## Data

The assistant answers from public health plan **Summary of Benefits and Coverage (SBC)** documents. Every US health plan must publish one in the same standard format, which makes them good test material: same structure, different numbers.

The PDFs are not stored in Git. [`data/sources.csv`](data/sources.csv) lists each document and where it came from, and `scripts/download_data.py` downloads them, so anyone gets the same set.

[`evals/seed_questions.csv`](evals/seed_questions.csv) holds 10 real questions a customer would ask. They guide what the system must handle and become the start of the test set in step 5.

## Progress

- [x] Step 1: Repo, environment and README
- [ ] Step 2: Collect policy documents and real user questions
- [ ] Step 3: Ingest documents into a vector database
- [ ] Step 4: Answer with citations
- [ ] Step 5: Test set and baseline metrics
- [ ] Step 6: Hybrid search and re-ranking
- [ ] Step 7: Streamlit web app
- [ ] Step 8: CI eval gate
- [ ] Step 9: Final write-up and demo

## Build log

Decisions and trade-offs for each step are recorded in [docs/build-log.md](docs/build-log.md).
