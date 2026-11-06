"""
search_engine
=============

A small, modular boolean/wildcard search engine with a Tkinter GUI.

Modules:
    document_loader     - load raw documents from disk
    tokenizer           - split raw text into tokens
    normalizer          - case-fold / clean tokens
    index_builder        - build an inverted index from documents
    query_processor      - parse and evaluate boolean queries (AND/OR/NOT)
    wildcard_processor   - expand '*' wildcard terms against the vocabulary
    gui                  - Tkinter front end tying everything together
"""

__version__ = "1.0.0"
