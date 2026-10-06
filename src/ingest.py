"""Step 3: read the policy PDFs, split them into chunks, embed them, and store them in ChromaDB.

Each chunk keeps the file name and page number it came from, so answers can cite them.
Running the script again rebuilds the collection from scratch.

Usage:
    python src/ingest.py
"""

import csv
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
SOURCES = ROOT / "data" / "sources.csv"
DB_DIR = ROOT / "chroma_db"
COLLECTION = "policies"

# ModernBERT embed reads up to 8192 tokens, so a 600-token chunk is embedded in full.
# (Many small models stop at 256 tokens and silently ignore the rest.)
EMBED_MODEL = "nomic-ai/modernbert-embed-base"
# This model expects a prefix saying whether the text is a document or a query.
DOC_PREFIX = "search_document: "
QUERY_PREFIX = "search_query: "  # used at question time (step 4)

CHUNK_TOKENS = 600
OVERLAP_TOKENS = 100


def load_sources() -> dict[str, dict]:
    """Issuer and plan name for each file, from data/sources.csv."""
    with SOURCES.open(newline="", encoding="utf-8") as f:
        return {row["file_name"]: row for row in csv.DictReader(f)}


def read_pages(pdf_path: Path) -> list[tuple[int, str]]:
    """Return (page_number, text) for each page that has text. Page numbers start at 1."""
    reader = PdfReader(pdf_path)
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:  # skip blank or image-only pages
            pages.append((number, text))
    return pages


def main() -> None:
    pdfs = sorted(RAW_DIR.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs in {RAW_DIR}. Run: python scripts/download_data.py")

    print(f"Loading embedding model {EMBED_MODEL} (first run downloads it)...")
    model = SentenceTransformer(EMBED_MODEL)

    # Measure chunk size with the embedding model's own tokenizer.
    splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        model.tokenizer, chunk_size=CHUNK_TOKENS, chunk_overlap=OVERLAP_TOKENS
    )
    sources = load_sources()

    # Split page by page so every chunk belongs to exactly one page.
    ids, texts, metadatas = [], [], []
    for pdf in pdfs:
        info = sources.get(pdf.name, {})
        pages = read_pages(pdf)
        before = len(texts)
        for page_number, page_text in pages:
            for i, chunk in enumerate(splitter.split_text(page_text)):
                ids.append(f"{pdf.stem}-p{page_number}-c{i}")
                texts.append(chunk)
                metadatas.append({
                    "file_name": pdf.name,
                    "page": page_number,
                    "issuer": info.get("issuer", ""),
                    "plan": info.get("plan", ""),
                })
        print(f"read      {pdf.name}: {len(pages)} pages -> {len(texts) - before} chunks")

    print(f"\nEmbedding {len(texts)} chunks...")
    embeddings = model.encode(
        [DOC_PREFIX + t for t in texts], batch_size=16, show_progress_bar=True
    )

    # Start fresh each run so re-ingesting never leaves stale or duplicate chunks.
    client = chromadb.PersistentClient(path=str(DB_DIR))
    if COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)
    collection = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings.tolist())

    print(f"\nStored {collection.count()} chunks from {len(pdfs)} PDFs in {DB_DIR}")

    # Quick check: run one search so you can see retrieval working.
    question = "What is the deductible?"
    query = model.encode([QUERY_PREFIX + question]).tolist()
    hits = collection.query(query_embeddings=query, n_results=3)
    print(f'\nSample search: "{question}"')
    for meta, text in zip(hits["metadatas"][0], hits["documents"][0]):
        snippet = " ".join(text.split())[:100]
        print(f"  [{meta['file_name']}, p.{meta['page']}] {snippet}...")


if __name__ == "__main__":
    main()
