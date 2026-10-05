"""Download the public policy PDFs listed in data/sources.csv into data/raw/.

The PDFs are not stored in Git (they belong to the insurers and can change),
so anyone who clones the repo runs this script to get the same documents.

Usage:
    python scripts/download_data.py
"""

import csv
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "sources.csv"
RAW_DIR = ROOT / "data" / "raw"

# Some insurer websites reject requests that don't look like a browser.
HEADERS = {"User-Agent": "Mozilla/5.0 (policy-rag-assistant data download)"}


def download(url: str, dest: Path) -> None:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read()
    # Every real PDF starts with "%PDF". Anything else is usually an error page.
    if not content.startswith(b"%PDF"):
        raise ValueError("response is not a PDF")
    dest.write_bytes(content)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with SOURCES.open(newline="", encoding="utf-8") as f:
        sources = list(csv.DictReader(f))

    failed = []
    for row in sources:
        dest = RAW_DIR / row["file_name"]
        if dest.exists():
            print(f"skip      {dest.name} (already downloaded)")
            continue
        try:
            download(row["url"], dest)
            print(f"saved     {dest.name} ({dest.stat().st_size // 1024} KB)")
        except Exception as error:  # keep going so one bad link doesn't stop the rest
            failed.append(row["file_name"])
            print(f"FAILED    {row['file_name']}: {error}")

    print(f"\n{len(sources) - len(failed)} of {len(sources)} documents are in {RAW_DIR}")
    if failed:
        print("For each failed file, open its URL from data/sources.csv in a browser,")
        print("save the PDF into data/raw/ with the file_name shown, or replace the row with another plan.")


if __name__ == "__main__":
    main()
