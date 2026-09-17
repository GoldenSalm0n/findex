import re
import unicodedata
from collections.abc import Iterator

TOKEN_PATTERN = re.compile(r"\w+(?:'\w+)?")


def tokenize(text: str) -> Iterator[str]:
    """Normalization"""
    if not text:
        return

    # Unicode NFC normalization.
    normalized_text = unicodedata.normalize("NFC", text)

    # Casefold for case-insensitivity.
    folded_text = normalized_text.casefold()

    # Lazy token generation using re.finditer
    for match in TOKEN_PATTERN.finditer(folded_text):
        yield match.group(0)

