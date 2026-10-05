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
- **Problems hit:** (fill in, e.g. links that didn't download)
