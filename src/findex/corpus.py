import json
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

logger = logging.getLogger(__name__)


class Document(NamedTuple):
    """Individual document from the corpus"""
    doc_id: int
    path: str
    text: str


def iter_documents(root: Path) -> Iterator[Document]:
    """Reads a corpus of documents"""
    if not root.exists():
        raise FileNotFoundError(f"Wrong root: {root}")

    doc_id = 0

    # Solo .jsonl file
    if root.is_file() and root.suffix == ".jsonl":
        yield from _stream_jsonl(root, start_id=doc_id)
        return

    # Dir
    if root.is_dir():
        # Finding .jsonl
        jsonl_files = sorted(root.glob("*.jsonl"))
        if jsonl_files:
            for file_path in jsonl_files:
                for doc in _stream_jsonl(file_path, start_id=doc_id):
                    yield doc
                    doc_id += 1
            return

        # No jsonl? --> .txt
        for file_path in sorted(root.rglob("*.txt")):
            try:
                text = file_path.read_text(encoding="utf-8", errors="replace").strip()
                if text:
                    yield Document(doc_id=doc_id, path=str(file_path), text=text)
                    doc_id += 1
            except Exception as exc:
                logger.warning("File reading error %s: %s", file_path, exc)
                continue


def _stream_jsonl(path: Path, start_id: int = 0) -> Iterator[Document]:
    """Lazy document stream"""
    current_id = start_id
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                text = data.get("text", "")
                if not text:
                    continue

                yield Document(
                    doc_id=data.get("doc_id", current_id),
                    path=data.get("path", f"{path.name}:{line_num}"),
                    text=text,
                )
                current_id += 1
            except json.JSONDecodeError as exc:
                logger.warning("Invalid JSON passed in %s:%d: %s", path.name, line_num, exc)
                continue