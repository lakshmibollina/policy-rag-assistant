# Policy RAG Assistant

Document Q&A with citations, built like a production system — not a demo.

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
pip install -r requirements.txt
```

## Roadmap

- [ ] Basic RAG: load PDFs, chunk, embed into ChromaDB, answer with citations
- [ ] 50-question eval set; score baseline
- [ ] Hybrid search + re-ranking; score again
- [ ] Web UI (Streamlit/Gradio) + GitHub Action running evals
