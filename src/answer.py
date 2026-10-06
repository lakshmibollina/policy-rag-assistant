"""Step 4: answer a question from the policy documents, with citations.

Usage:
    python src/answer.py "Is physical therapy covered?"
"""

import sys
import time

import chromadb
import ollama
from sentence_transformers import SentenceTransformer

from ingest import COLLECTION, DB_DIR, EMBED_MODEL, QUERY_PREFIX, ROOT

LLM = "llama3.2"
TOP_K = 5
PROMPT = (ROOT / "prompts" / "answer_v1.txt").read_text(encoding="utf-8")

embedder = SentenceTransformer(EMBED_MODEL)
collection = chromadb.PersistentClient(path=str(DB_DIR)).get_collection(COLLECTION)


def answer(question: str) -> str:
    query = embedder.encode(QUERY_PREFIX + question).tolist()
    hits = collection.query(query_embeddings=[query], n_results=TOP_K)

    # Label each chunk with the exact citation the model should copy.
    context = "\n\n".join(
        f"[{meta['file_name']}, p.{meta['page']}]\n{text}"
        for meta, text in zip(hits["metadatas"][0], hits["documents"][0])
    )
    response = ollama.chat(
        model=LLM,
        messages=[{"role": "user", "content": PROMPT.format(context=context, question=question)}],
        # Ollama's default context window is too small for 5 x 600-token chunks.
        options={"temperature": 0, "num_ctx": 8192},
    )
    return response.message.content


if __name__ == "__main__":
    start = time.perf_counter()
    print(answer(sys.argv[1]))
    print(f"\n({time.perf_counter() - start:.1f}s)")
