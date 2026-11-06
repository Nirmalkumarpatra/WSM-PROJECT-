"""
main.py
-------
Entry point. Wires the pipeline together:

    document_loader -> index_builder -> gui (which uses query_processor
    and wildcard_processor internally on each search).

Run with:
    python -m search_engine.main [optional_docs_directory]
"""

from __future__ import annotations

import os
import sys

from .document_loader import load_documents_from_dir
from .index_builder import InvertedIndex
from .gui import launch_gui

DEFAULT_DOCS_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")


def main() -> None:
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DOCS_DIR

    documents = load_documents_from_dir(docs_dir)

    index = InvertedIndex()
    index.build(documents)

    print(f"Indexed {len(index)} document(s) from '{docs_dir}' "
          f"({len(index.vocabulary())} unique terms).")

    launch_gui(index)


if __name__ == "__main__":
    main()
