"""Textual workspace dashboard.

Read-only views over the BugBountyOS workflow plane:
    Scope -> Assets -> Inputs -> Findings -> Reports
"""
from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, TabbedContent, TabPane

from bbos.tui.views import (
    AssetsView,
    FindingsView,
    InputsView,
    ReportsView,
    ScopeView,
)


class WorkspaceApp(App):
    CSS = """
    Screen { layout: vertical; }
    TabbedContent { height: 1fr; }
    DataTable { height: 1fr; }
    .caption { padding: 0 1; color: $text-muted; }
    """

    TITLE = "BugBountyOS - Workspace"
    SUB_TITLE = "read-only"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("1", "show('scope')", "Scope"),
        Binding("2", "show('assets')", "Assets"),
        Binding("3", "show('inputs')", "Inputs"),
        Binding("4", "show('findings')", "Findings"),
        Binding("5", "show('reports')", "Reports"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            with TabbedContent(initial="scope", id="tabs"):
                with TabPane("Scope", id="scope"):
                    yield ScopeView()
                with TabPane("Assets", id="assets"):
                    yield AssetsView()
                with TabPane("Inputs", id="inputs"):
                    yield InputsView()
                with TabPane("Findings", id="findings"):
                    yield FindingsView()
                with TabPane("Reports", id="reports"):
                    yield ReportsView()
        yield Footer()

    def action_show(self, tab_id: str) -> None:
        self.query_one("#tabs", TabbedContent).active = tab_id
