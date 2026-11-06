"""
normalizer.py
-------------
Responsible for ONE thing: turning a raw token into its normalized form
that gets stored in / looked up from the index.

Currently performs:
    - case folding (lowercasing)
    - optional stopword removal
    - optional digit-only token filtering

Kept as small pure functions so it's easy to unit test and to extend
(e.g. with stemming/lemmatization) without touching tokenizer or index code.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Set

# A small default stopword list. Pass stopwords=None to disable filtering.
DEFAULT_STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "of", "to", "in", "on",
    "for", "with", "is", "are", "was", "were", "be", "been", "it", "this",
    "that", "as", "at", "by", "from",
}


def normalize_token(token: str) -> str:
    """Case-fold a single token (lowercase). This is the canonical form
    used as a key in the inverted index."""
    return token.lower()


def normalize_tokens(
    tokens: Iterable[str],
    stopwords: Optional[Set[str]] = DEFAULT_STOPWORDS,
    min_length: int = 1,
) -> List[str]:
    """
    Normalize a sequence of raw tokens: lowercase each, drop stopwords,
    and drop tokens shorter than `min_length`.

    Args:
        tokens: raw tokens, e.g. from tokenizer.tokenize()
        stopwords: set of words to exclude, or None to keep everything
        min_length: minimum token length to keep (filters noise like "s")

    Returns:
        list of normalized tokens, in original order, stopwords/short
        tokens removed.
    """
    normalized = []
    stopset = stopwords or set()
    for tok in tokens:
        norm = normalize_token(tok)
        if len(norm) < min_length:
            continue
        if norm in stopset:
            continue
        normalized.append(norm)
    return normalized
