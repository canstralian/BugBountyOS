"""Tab panes for the workspace dashboard."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Static

from bbos.data import load_contracts, load_vectors


class ScopeView(Vertical):
    """Authorized vectors from the control-plane registry."""

    def compose(self) -> ComposeResult:
        yield Static(
            "Authorized vectors (control-plane/registry/vectors.yaml). "
            "Scope is enforced upstream by the Airtable Immune System.",
            classes="caption",
        )
        table: DataTable = DataTable(zebra_stripes=True)
        table.add_columns("id", "role", "state", "trust", "source")
        for v in load_vectors():
            table.add_row(v.id, v.role, v.state, v.trust_level, v.source_repo)
        yield table


class AssetsView(Vertical):
    """Output types each vector produces (asset graph node shapes)."""

    def compose(self) -> ComposeResult:
        yield Static(
            "Output interfaces declared per vector contract.",
            classes="caption",
        )
        table: DataTable = DataTable(zebra_stripes=True)
        table.add_columns("vector", "type", "description")
        for c in load_contracts():
            for o in c.outputs:
                table.add_row(c.vector_id, o.type, o.description)
        yield table


class InputsView(Vertical):
    """Input types each vector consumes (input map)."""

    def compose(self) -> ComposeResult:
        yield Static(
            "Input interfaces declared per vector contract.",
            classes="caption",
        )
        table: DataTable = DataTable(zebra_stripes=True)
        table.add_columns("vector", "type", "description")
        for c in load_contracts():
            for i in c.inputs:
                table.add_row(c.vector_id, i.type, i.description)
        yield table


class FindingsView(Vertical):
    """Gate status by vector (the 5-gate promotion ledger)."""

    def compose(self) -> ComposeResult:
        yield Static(
            "Gate status per vector contract (see docs/CONTRACTS.md).",
            classes="caption",
        )
        table: DataTable = DataTable(zebra_stripes=True)
        table.add_columns("vector", "gate", "status")
        for c in load_contracts():
            for g in c.gates:
                table.add_row(c.vector_id, g.name or g.id, g.status)
        yield table


class ReportsView(Vertical):
    """Aggregate roll-up across the workspace."""

    def compose(self) -> ComposeResult:
        vectors = load_vectors()
        contracts = load_contracts()
        total_gates = sum(len(c.gates) for c in contracts)
        completed = sum(
            1 for c in contracts for g in c.gates if g.status == "completed"
        )

        states: dict[str, int] = {}
        for v in vectors:
            states[v.state] = states.get(v.state, 0) + 1

        lines = [
            f"Vectors registered: {len(vectors)}",
            f"Contracts on disk:  {len(contracts)}",
            f"Gates completed:    {completed}/{total_gates}",
            "",
            "Lifecycle states:",
        ]
        for state, n in sorted(states.items()):
            lines.append(f"  {state}: {n}")
        yield Static("\n".join(lines))
