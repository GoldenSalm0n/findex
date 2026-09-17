from pathlib import Path
from findex.corpus import iter_documents, Document


def test_stream_first_document():
    path = Path("data/corpus.jsonl")
    stream = iter_documents(path)
    doc = next(stream)

    assert isinstance(doc, Document)
    assert doc.doc_id >= 0
    assert len(doc.text) > 0
    print(f"\n[OK] Doc ID: {doc.doc_id}, Length: {len(doc.text)} chars")