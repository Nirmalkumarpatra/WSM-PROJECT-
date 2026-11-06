"""
document_loader.py
-------------------
Responsible for ONE thing: getting raw document text into memory.

No tokenization, normalization, or indexing logic lives here - this module
only knows how to find documents and read their contents.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Iterable


@dataclass
class Document:
    """A single loaded document."""
    doc_id: str
    title: str
    text: str


class DocumentLoadError(Exception):
    """Raised when documents cannot be loaded from a given source."""


def load_documents_from_dir(directory: str, extensions: Iterable[str] = (".txt",)) -> Dict[str, Document]:
    """
    Load every file with a matching extension from `directory`.

    Each file becomes one Document. The doc_id is the filename (without
    extension); the title is the same as the doc_id unless the file's
    first line looks like a title (kept simple here: title == doc_id).

    Returns:
        dict mapping doc_id -> Document
    """
    if not os.path.isdir(directory):
        raise DocumentLoadError(f"'{directory}' is not a valid directory")

    documents: Dict[str, Document] = {}
    for filename in sorted(os.listdir(directory)):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in extensions:
            continue
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError as exc:
            raise DocumentLoadError(f"Could not read '{filepath}': {exc}") from exc

        documents[name] = Document(doc_id=name, title=name, text=text)

    return documents


def load_documents_from_dict(raw: Dict[str, str]) -> Dict[str, Document]:
    """
    Convenience loader for in-memory documents, e.g. {"doc1": "some text"}.
    Useful for tests, demos, or when documents come from an API/database
    instead of the filesystem.
    """
    return {
        doc_id: Document(doc_id=doc_id, title=doc_id, text=text)
        for doc_id, text in raw.items()
    }
