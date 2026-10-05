# Project conventions

Policy RAG Assistant: question answering over health plan documents, with citations.

- Python 3.11+. Keep code simple and readable, with short comments.
- Secrets are read from `.env` with python-dotenv and never committed.
- Documents are listed in `data/sources.csv` and downloaded with `scripts/download_data.py`; PDFs are not committed.
- Record design decisions and measured results in `docs/build-log.md`.
- Keep the README's Status and Progress sections current.
