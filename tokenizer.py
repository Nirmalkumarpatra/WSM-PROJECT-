"""
tokenizer.py
------------
Responsible for ONE thing: splitting raw text into a sequence of raw tokens.

Deliberately does NOT lowercase or strip punctuation beyond what's needed to
split words apart - that belongs in normalizer.py. Keeping this split makes
it easy to swap in a smarter tokenizer (e.g. regex, NLTK, spaCy) later
without touching normalization or indexing code.
"""

from __future__ import annotations

import re
from typing import List

# Matches runs of alphanumeric characters (keeps internal apostrophes/hyphens
# out of the token boundary so "don't" -> "don", "t" - simple and predictable).
_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")


def tokenize(text: str) -> List[str]:
    """
    Split `text` into a list of raw word tokens.

    Example:
        tokenize("The Quick-Brown fox's box.") ->
            ["The", "Quick", "Brown", "fox", "s", "box"]
    """
    if not text:
        return []
    return _TOKEN_PATTERN.findall(text)
