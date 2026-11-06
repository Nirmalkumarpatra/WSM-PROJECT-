"""
gui.py
------
Responsible for ONE thing: the Tkinter front end. It wires user input to
query_processor.parse_and_search() and renders results - it contains no
tokenization, normalization, or indexing logic of its own.

Layout:
    [ search entry box ][ Search button ]
    [ read-only, scrollable result area              ]
"""

from __future__ import annotations

import tkinter as tk
from tkinter import scrolledtext, ttk

from .index_builder import InvertedIndex
from .query_processor import QueryError, parse_and_search

_HELP_TEXT = (
    "Examples:\n"
    "  python           - all docs containing 'python'\n"
    "  cat AND dog       - docs containing both terms\n"
    "  cat OR dog        - docs containing either term\n"
    "  cat AND NOT dog   - docs with 'cat' but not 'dog'\n"
    "  prog*             - wildcard match (program, programming, ...)\n"
)


class SearchApp(tk.Tk):
    """Main application window."""

    def __init__(self, index: InvertedIndex) -> None:
        super().__init__()
        self.index = index

        self.title("Inverted Index Search Engine")
        self.geometry("760x520")
        self.minsize(560, 400)

        self._build_widgets()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #
    def _build_widgets(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        # --- search row: entry box + Search button -----------------------
        search_row = ttk.Frame(container)
        search_row.pack(fill=tk.X, pady=(0, 8))

        self.query_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_row, textvariable=self.query_var, font=("Segoe UI", 11))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.search_entry.bind("<Return>", lambda _event: self.run_search())
        self.search_entry.focus_set()

        self.search_button = ttk.Button(search_row, text="Search", command=self.run_search)
        self.search_button.pack(side=tk.LEFT, padx=(8, 0))

        # --- status line ---------------------------------------------------
        self.status_var = tk.StringVar(value=f"{len(self.index)} document(s) indexed. Ready.")
        status_label = ttk.Label(container, textvariable=self.status_var, foreground="#555555")
        status_label.pack(fill=tk.X, pady=(0, 8))

        # --- read-only result area -----------------------------------------
        self.result_area = scrolledtext.ScrolledText(
            container, wrap=tk.WORD, font=("Consolas", 10), state=tk.DISABLED
        )
        self.result_area.pack(fill=tk.BOTH, expand=True)

        self._set_result_text(_HELP_TEXT)

    # ------------------------------------------------------------------ #
    # Behavior
    # ------------------------------------------------------------------ #
    def _set_result_text(self, text: str) -> None:
        """Write to the result area while keeping it read-only to the user."""
        self.result_area.configure(state=tk.NORMAL)
        self.result_area.delete("1.0", tk.END)
        self.result_area.insert(tk.END, text)
        self.result_area.configure(state=tk.DISABLED)

    def run_search(self) -> None:
        query = self.query_var.get()
        try:
            doc_ids = parse_and_search(query, self.index)
        except QueryError as exc:
            self.status_var.set(f"Error: {exc}")
            self._set_result_text(_HELP_TEXT)
            return

        self.status_var.set(f"{len(doc_ids)} result(s) for: {query!r}")

        if not doc_ids:
            self._set_result_text("No documents matched your query.")
            return

        lines = []
        for doc_id in doc_ids:
            document = self.index.documents[doc_id]
            snippet = " ".join(document.text.split())[:160]
            lines.append(f"[{doc_id}] {document.title}\n    {snippet}...\n")
        self._set_result_text("\n".join(lines))


def launch_gui(index: InvertedIndex) -> None:
    """Convenience entry point: build and start the Tkinter event loop."""
    app = SearchApp(index)
    app.mainloop()
