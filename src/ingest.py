"""Step 3: chunk the policy PDFs, embed the chunks, and store them in ChromaDB.

Usage:
    python src/ingest.py
"""

import shutil
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
DB_DIR = ROOT / "chroma_db"
COLLECTION = "policies"

# Reads up to 8192 tokens, so 600-token chunks are embedded in full.
EMBED_MODEL = "nomic-ai/modernbert-embed-base"
# The model expects these prefixes on documents and queries.
DOC_PREFIX = "search_document: "
QUERY_PREFIX = "search_query: "


def main() -> None:
    model = SentenceTransformer(EMBED_MODEL)
    # Count tokens with the embedding model's own tokenizer.
    splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        model.tokenizer, chunk_size=600, chunk_overlap=100
    )

    # Split each page separately so every chunk has a single page to cite.
    ids, texts, metadatas = [], [], []
    for pdf in sorted(RAW_DIR.glob("*.pdf")):
        for page_number, page in enumerate(PdfReader(pdf).pages, start=1):
            for i, chunk in enumerate(splitter.split_text(page.extract_text() or "")):
                ids.append(f"{pdf.stem}-p{page_number}-c{i}")
                texts.append(chunk)
                metadatas.append({"file_name": pdf.name, "page": page_number})

    embeddings = model.encode([DOC_PREFIX + t for t in texts], show_progress_bar=True)

    # Rebuild from scratch so re-runs never leave stale chunks.
    shutil.rmtree(DB_DIR, ignore_errors=True)
    collection = chromadb.PersistentClient(path=str(DB_DIR)).create_collection(
        COLLECTION, metadata={"hnsw:space": "cosine"}
    )
    collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings.tolist())
    print(f"Stored {collection.count()} chunks in {DB_DIR}")


if __name__ == "__main__":
    main()
