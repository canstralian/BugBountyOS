"""Read-only loaders for the BugBountyOS workspace.

The control-plane registry and per-vector contracts ship base64-encoded on
disk (see CLAUDE.md). These helpers transparently decode either form so the
TUI can render whichever the working tree currently holds.
"""
from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "control-plane" / "registry" / "vectors.yaml"
CONTRACTS_DIR = REPO_ROOT / "contracts"


def _decode_yaml_bytes(raw: bytes) -> dict[str, Any]:
    # Most YAML on disk in this repo is base64-encoded with line wrapping;
    # strip whitespace before validating, then fall back to plain YAML.
    stripped = raw.translate(bytes.maketrans(b"", b""), b"\r\n\t ")
    try:
        candidate = base64.b64decode(stripped, validate=True).decode("utf-8")
        parsed = yaml.safe_load(candidate)
        if isinstance(parsed, dict):
            return parsed
    except (binascii.Error, UnicodeDecodeError, yaml.YAMLError):
        pass
    parsed = yaml.safe_load(raw.decode("utf-8")) or {}
    return parsed if isinstance(parsed, dict) else {}


@dataclass(frozen=True)
class Vector:
    id: str
    role: str
    state: str
    trust_level: str
    source_repo: str
    contract_version: int


@dataclass(frozen=True)
class Gate:
    id: str
    name: str
    status: str


@dataclass(frozen=True)
class Interface:
    type: str
    description: str


@dataclass(frozen=True)
class Contract:
    vector_id: str
    role: str
    description: str
    version: str
    gates: tuple[Gate, ...] = field(default_factory=tuple)
    inputs: tuple[Interface, ...] = field(default_factory=tuple)
    outputs: tuple[Interface, ...] = field(default_factory=tuple)


def load_vectors(registry_path: Path = REGISTRY_PATH) -> list[Vector]:
    if not registry_path.exists():
        return []
    data = _decode_yaml_bytes(registry_path.read_bytes())
    out: list[Vector] = []
    for raw in data.get("vectors", []) or []:
        out.append(
            Vector(
                id=str(raw.get("id") or ""),
                role=str(raw.get("role") or ""),
                state=str(raw.get("state") or ""),
                trust_level=str(raw.get("trust_level") or ""),
                source_repo=str(raw.get("source_repo") or ""),
                contract_version=int(raw.get("contract_version", 0) or 0),
            )
        )
    return out


def load_contracts(contracts_dir: Path = CONTRACTS_DIR) -> list[Contract]:
    if not contracts_dir.exists():
        return []
    contracts: list[Contract] = []
    for path in sorted(contracts_dir.glob("*.yaml")):
        raw = _decode_yaml_bytes(path.read_bytes())
        gates = tuple(
            Gate(
                id=str(g.get("id", "")),
                name=str(g.get("name", "")),
                status=str(g.get("status", "")),
            )
            for g in raw.get("gates", []) or []
        )
        interfaces = raw.get("interfaces") or {}
        inputs = tuple(
            Interface(
                # Tolerate the `t^e` typo currently present in recon.yaml.
                type=str(i.get("type") or i.get("t^e") or ""),
                description=str(i.get("description", "")),
            )
            for i in interfaces.get("input", []) or []
        )
        outputs = tuple(
            Interface(
                type=str(i.get("type", "")),
                description=str(i.get("description", "")),
            )
            for i in interfaces.get("output", []) or []
        )
        contracts.append(
            Contract(
                vector_id=str(raw.get("vector_id") or path.stem),
                role=str(raw.get("role", "")),
                description=str(raw.get("description", "")),
                version=str(raw.get("version", "")),
                gates=gates,
                inputs=inputs,
                outputs=outputs,
            )
        )
    return contracts
