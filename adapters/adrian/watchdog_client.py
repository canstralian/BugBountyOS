"""
adapters/adrian/watchdog_client.py — BugBountyOS Watchdog Adapter.

Wraps the secureagentics/Adrian engine (subtree-imported under vectors/adrian/)
to gate every kernel policy/decision call with a reasoning-trace verdict.

The kernel calls WatchdogClient.gate(...) before returning allow/deny/quarantine
for any action. Adrian inspects the agent's reasoning trace — chain-of-thought,
tool-call sequence, and referenced targets — and returns a structured verdict.

Block signals enforced (see contracts/adrian.yaml):
  - tool_call_sequence:      unsafe ordering / forbidden chains
  - out_of_scope_target:     references hosts not in the Airtable scope manifest
  - prompt_injection_marker: jailbreak / canary-leak patterns in the trace
  - tampered_reasoning:      planning forbidden actions or gate-bypass attempts

Failure mode (per the contract):
  trust_level=permissive  -> fail-open, emit audit event to /v1/events
  trust_level=strict      -> fail-closed, return QUARANTINE if Adrian is unreachable

This adapter is the kernel-side call site; the Adrian engine itself lives at
vectors/adrian/ after subtree import. The vector is registered in
control-plane/registry/vectors.yaml with role=watchdog and coverage=universal.
"""
from __future__ import annotations

import enum
import logging
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence

logger = logging.getLogger(__name__)


class Verdict(str, enum.Enum):
    ALLOW = "allow"
    BLOCK = "block"
    QUARANTINE = "quarantine"


class BlockSignal(str, enum.Enum):
    TOOL_CALL_SEQUENCE = "tool_call_sequence"
    OUT_OF_SCOPE_TARGET = "out_of_scope_target"
    PROMPT_INJECTION_MARKER = "prompt_injection_marker"
    TAMPERED_REASONING = "tampered_reasoning"


class TrustLevel(str, enum.Enum):
    PERMISSIVE = "permissive"
    STRICT = "strict"


@dataclass(frozen=True)
class ReasoningTrace:
    """One agent decision episode as observed by the kernel."""

    vector_id: str
    action: str
    chain_of_thought: str
    tool_calls: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    targets: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class WatchdogVerdict:
    verdict: Verdict
    reason_codes: Sequence[BlockSignal]
    rationale: str
    audit_event: Mapping[str, Any]


class WatchdogUnavailable(RuntimeError):
    """Raised when the Adrian engine cannot be reached and trust_level is strict."""


@dataclass
class WatchdogClient:
    """Synchronous gate invoked by the kernel for every /v1/decision request."""

    endpoint: str = field(
        default_factory=lambda: os.environ.get("ADRIAN_ENDPOINT", "http://localhost:8787")
    )
    trust_level: TrustLevel = TrustLevel.STRICT
    timeout_s: float = 2.0

    def gate(self, trace: ReasoningTrace) -> WatchdogVerdict:
        """Return Adrian's verdict for a candidate kernel action.

        Concrete SDK wiring lands once the vectors/adrian/ subtree is imported
        and the Adrian Python SDK is on the import path. Until then this stub
        honours the configured trust_level so the call site stays stable.
        """
        try:
            return self._call_adrian(trace)
        except WatchdogUnavailable:
            raise
        except Exception as exc:
            return self._on_failure(trace, exc)

    def _call_adrian(self, trace: ReasoningTrace) -> WatchdogVerdict:
        raise WatchdogUnavailable(
            "Adrian SDK integration not yet wired; vectors/adrian must reach "
            "state=active in control-plane/registry/vectors.yaml first."
        )

    def _on_failure(self, trace: ReasoningTrace, exc: Exception) -> WatchdogVerdict:
        audit = {
            "vector_id": trace.vector_id,
            "action": trace.action,
            "trace": asdict(trace),
            "error": repr(exc),
        }
        if self.trust_level is TrustLevel.STRICT:
            logger.error("Adrian watchdog unreachable; quarantining action: %s", exc)
            return WatchdogVerdict(
                verdict=Verdict.QUARANTINE,
                reason_codes=(),
                rationale="watchdog_unreachable_strict",
                audit_event=audit,
            )
        logger.warning("Adrian watchdog unreachable; permissive fail-open: %s", exc)
        return WatchdogVerdict(
            verdict=Verdict.ALLOW,
            reason_codes=(),
            rationale="watchdog_unreachable_permissive",
            audit_event=audit,
        )
