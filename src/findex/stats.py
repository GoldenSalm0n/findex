import argparse
import itertools
import time
import tracemalloc
from collections import Counter
from pathlib import Path
from typing import NamedTuple

from findex.src.findex.corpus import iter_documents
from findex.src.findex.tokenize import tokenize


class CorpusStats(NamedTuple):
    doc_count: int
    token_count: int
    vocab_size: int
    top_terms: list[tuple[str, int]]
    elapsed_sec: float
    peak_ram_mb: float


def compute_stats(corpus_path: Path, limit: int | None = None) -> CorpusStats:
    """Calculates corpus statistics in a single pass."""
    tracemalloc.start()
    start_time = time.perf_counter()

    doc_stream = iter_documents(corpus_path)
    if limit is not None:
        doc_stream = itertools.islice(doc_stream, limit)

    doc_count = 0
    token_count = 0
    term_counts: Counter[str] = Counter()

    for doc in doc_stream:
        doc_count += 1
        for token in tokenize(doc.text):
            token_count += 1
            term_counts[token] += 1

    elapsed_sec = time.perf_counter() - start_time
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_ram_mb = peak_bytes / (1024 * 1024)

    return CorpusStats(
        doc_count=doc_count,
        token_count=token_count,
        vocab_size=len(term_counts),
        top_terms=term_counts.most_common(50),
        elapsed_sec=elapsed_sec,
        peak_ram_mb=peak_ram_mb,
    )


def main() -> None:
    default_corpus_path = Path(__file__).resolve().parents[2] / "data" / "corpus.jsonl"
    default_limit = 500

    parser = argparse.ArgumentParser(
        description="Compute corpus statistics using a lazy streaming pipeline."
    )
    parser.add_argument(
        "corpus",
        type=Path,
        nargs="?",
        default=default_corpus_path,
        help="Path to a .jsonl file or directory containing the corpus.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=default_limit,
        help="Limit the number of processed documents",
    )
    args = parser.parse_args()

    print(f"Corpus analysis: {args.corpus} (limit={args.limit})...\n")
    stats = compute_stats(args.corpus, limit=args.limit)

    print(f"Documents processed      : {stats.doc_count:,}")
    print(f"Total token count        : {stats.token_count:,}")
    print(f"Vocabulary size          : {stats.vocab_size:,}")
    print(f"Execution time           : {stats.elapsed_sec:.2f} seconds")
    print(f"Peak memory (RAM)        : {stats.peak_ram_mb:.2f} MB\n")

    print("Top 50 most frequent terms:")
    print(f"{'#':<4}{'Term':<25}{'Frequency':>10}")
    print("-" * 39)
    for rank, (term, count) in enumerate(stats.top_terms, start=1):
        print(f"{rank:<4}{term:<25}{count:>10,}")


if __name__ == "__main__":
    main()