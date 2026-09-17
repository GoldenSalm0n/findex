import json
import re
import time
import tracemalloc
import unicodedata
from collections import Counter
from pathlib import Path
from typing import NamedTuple

from findex.stats import compute_stats

TOKEN_PATTERN = re.compile(r"\w+(?:'\w+)?")
APOSTROPHE_TRANSLATION = str.maketrans("’ʼ`´", "''''")


class Document(NamedTuple):
    doc_id: int
    path: str
    text: str


def run_eager(corpus_path: Path, limit: int | None = None):
    """eager"""
    tracemalloc.start()
    start_time = time.perf_counter()

    # In RAM
    documents: list[Document] = []
    with corpus_path.open("r", encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, start=1):
            if limit is not None and len(documents) >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                text = data.get("text", "")
                if text:
                    documents.append(
                        Document(
                            doc_id=data.get("doc_id", len(documents)),
                            path=data.get("path", f"{corpus_path.name}:{line_num}"),
                            text=text,
                        )
                    )
            except json.JSONDecodeError:
                continue

    # Tokens in lists
    all_tokens: list[list[str]] = []
    for doc in documents:
        norm = unicodedata.normalize("NFC", doc.text).casefold()
        cleaned = norm.translate(APOSTROPHE_TRANSLATION)
        doc_tokens = [m.group(0) for m in TOKEN_PATTERN.finditer(cleaned)]
        all_tokens.append(doc_tokens)

    # Stats
    token_count = 0
    term_counts: Counter[str] = Counter()
    for doc_tokens in all_tokens:
        token_count += len(doc_tokens)
        term_counts.update(doc_tokens)

    elapsed_sec = time.perf_counter() - start_time
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "docs": len(documents),
        "tokens": token_count,
        "vocab": len(term_counts),
        "time": elapsed_sec,
        "ram_mb": peak_bytes / (1024 * 1024),
    }


def main():
    corpus = Path("data/corpus.jsonl")
    # If an Out-of-Memory error occurs, you can specify a limit.
    limit = None

    print("Running Eager version...")
    eager_res = run_eager(corpus, limit=limit)

    print("Running Lazy version...")
    lazy_res = compute_stats(corpus, limit=limit)

    print("\n" + "=" * 55)
    print(f"{'Version':<18}{'Documents':<12}{'Peak RAM':<14}{'Elapsed'}")
    print("-" * 55)
    print(
        f"{'eager (lists)':<18}{eager_res['docs']:<12}{eager_res['ram_mb']:.2f} MB      {eager_res['time']:.2f} s"
    )
    print(
        f"{'lazy (generators)':<18}{lazy_res.doc_count:<12}{lazy_res.peak_ram_mb:.2f} MB         {lazy_res.elapsed_sec:.2f} s"
    )
    print("=" * 55)


if __name__ == "__main__":
    main()