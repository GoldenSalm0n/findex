import inspect
from findex.tokenize import tokenize


def test_is_generator():
    """Tokenize is generator?"""
    assert inspect.isgeneratorfunction(tokenize)
    gen = tokenize("Test text")
    assert inspect.isgenerator(gen)


def test_empty_and_whitespace():
    """An empty string or spaces = don't yield any tokens"""
    assert list(tokenize("")) == []
    assert list(tokenize("   \n\t  ")) == []


def test_mixed_case_and_casefold():
    """ß -> ss"""
    assert list(tokenize("Barça BARCELONA")) == ["barça", "barcelona"]
    assert list(tokenize("Fußball")) == ["fussball"]


def test_cyrillic():
    """Cytrilian"""
    assert list(tokenize("Динамо Київ перемагає")) == ["динамо", "київ", "перемагає"]


def test_combining_mark_accent_nfc():
    """Combining diacritical marks are normalized by NFC"""
    accented_e = "e\u0301"
    composed_e = "é"
    assert list(tokenize(accented_e)) == list(tokenize(composed_e)) == ["é"]


def test_apostrophe_policy():
    """Preservation of apostrophes."""
    text = "Don't м'яч комп'ютер"
    assert list(tokenize(text)) == ["don't", "м'яч", "комп'ютер"]


def test_hyphen_and_punctuation_policy():
    """Hyphens separate words, Punctuation = trash"""
    text = "Real-Madrid vs Chelsea: 1-3 (FT)!"
    assert list(tokenize(text)) == ["real", "madrid", "vs", "chelsea", "1", "3", "ft"]