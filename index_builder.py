"""
index_builder.py
-----------------
Responsible for ONE thing: building and holding the inverted index that
maps normalized terms -> the set of document IDs containing that term.

Depends on document_loader (for Document), tokenizer, and normalizer, but
knows nothing about query syntax or the GUI.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Set

from .document_loader import Document
from .normalizer import normalize_tokens
from .tokenizer import tokenize


class InvertedIndex:
    """
    A simple in-memory inverted index.

    Attributes:
        index: term -> set of doc_ids containing that term
        documents: doc_id -> Document (kept so query results can show
                   titles/snippets)
    """

    def __init__(self) -> None:
        self.index: Dict[str, Set[str]] = defaultdict(set)
        self.documents: Dict[str, Document] = {}

    def add_document(self, document: Document) -> None:
        """Tokenize, normalize, and index a single document."""
        self.documents[document.doc_id] = document
        raw_tokens = tokenize(document.text)
        for term in normalize_tokens(raw_tokens):
            self.index[term].add(document.doc_id)

    def build(self, documents: Dict[str, Document]) -> None:
        """Build (or rebuild) the index from a dict of doc_id -> Document."""
        self.index.clear()
        self.documents.clear()
        for document in documents.values():
            self.add_document(document)

    def postings(self, term: str) -> Set[str]:
        """Return the set of doc_ids containing the exact normalized term."""
        return self.index.get(term, set())

    def vocabulary(self) -> Set[str]:
        """Return the full set of indexed terms - used by wildcard_processor."""
        return set(self.index.keys())

    def all_doc_ids(self) -> Set[str]:
        """Return every doc_id in the index - used for NOT queries."""
        return set(self.documents.keys())

    def __len__(self) -> int:
        return len(self.documents)
