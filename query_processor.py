"""
query_processor.py
-------------------
Responsible for ONE thing: parsing a user's query string and evaluating it
against an InvertedIndex to produce a set of matching document IDs.

Supported query syntax (case-insensitive keywords, whitespace-separated):
    term1 AND term2
    term1 OR term2
    NOT term1
    term1 AND NOT term2
    a mix, evaluated strictly left-to-right, e.g.:
        "cat AND dog OR NOT fish"  ==  ((cat AND dog) OR (NOT fish))

    A bare multi-word query with no operators ("machine learning") is
    treated as an implicit AND of all terms.

    Any individual term may contain a '*' wildcard (see wildcard_processor),
    e.g. "prog* AND test"

This module delegates single-term lookup to InvertedIndex.postings() and
wildcard expansion to wildcard_processor.expand_wildcard(), so it never
touches raw text or postings storage directly.
"""

from __future__ import annotations

from typing import List, Set

from .index_builder import InvertedIndex
from .normalizer import normalize_token
from .wildcard_processor import expand_wildcard, is_wildcard_term

_OPERATORS = {"AND", "OR", "NOT"}


class QueryError(Exception):
    """Raised for malformed / empty queries."""


def _term_postings(term: str, index: InvertedIndex) -> Set[str]:
    """Resolve a single query term (possibly a wildcard) to a doc_id set."""
    if is_wildcard_term(term):
        matched_terms = expand_wildcard(term, index.vocabulary())
        result: Set[str] = set()
        for matched in matched_terms:
            result |= index.postings(matched)
        return result
    return index.postings(normalize_token(term))


def parse_and_search(query: str, index: InvertedIndex) -> List[str]:
    """
    Parse `query` and evaluate it against `index`.

    Returns:
        sorted list of matching doc_ids.

    Raises:
        QueryError if the query is empty or malformed.
    """
    if not query or not query.strip():
        raise QueryError("Query is empty.")

    raw_tokens = query.strip().split()

    # Normalize operator casing but leave terms (and their '*') untouched.
    tokens = [t.upper() if t.upper() in _OPERATORS else t for t in raw_tokens]

    # Insert implicit AND between two consecutive non-operator terms,
    # e.g. "machine learning" -> "machine AND learning"
    expanded: List[str] = []
    prev_was_term = False
    for tok in tokens:
        is_op = tok in _OPERATORS
        if prev_was_term and not is_op:
            expanded.append("AND")
        expanded.append(tok)
        prev_was_term = not is_op
    tokens = expanded

    result: Set[str] = set()
    pending_op = "OR"   # how the *next* term combines with `result`
    negate_next = False
    i = 0
    first_term = True

    while i < len(tokens):
        tok = tokens[i]

        if tok == "AND":
            pending_op = "AND"
        elif tok == "OR":
            pending_op = "OR"
        elif tok == "NOT":
            negate_next = True
        else:
            postings = _term_postings(tok, index)
            if negate_next:
                postings = index.all_doc_ids() - postings
                negate_next = False

            if first_term:
                result = postings
                first_term = False
            elif pending_op == "AND":
                result &= postings
            else:  # OR
                result |= postings
            pending_op = "OR"  # reset default combinator

        i += 1

    if first_term:
        # Query consisted only of operators, e.g. "AND OR"
        raise QueryError("Query must contain at least one search term.")

    return sorted(result)
