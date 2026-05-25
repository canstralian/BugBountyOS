"""Unit tests for the Adrian watchdog adapter's failure semantics.

The adapter is a stub until the Adrian SDK integration lands, but its
trust_level contract is load-bearing: an unreachable engine must fail closed
(quarantine) under strict trust and fail open (allow) under permissive trust,
and the kernel must always receive a verdict rather than an exception.
"""
from adapters.adrian import (
    ReasoningTrace,
    TrustLevel,
    Verdict,
    WatchdogClient,
)

TRACE = ReasoningTrace(
    vector_id="recon",
    action="enumerate",
    chain_of_thought="probe the target",
    tool_calls=({"name": "nmap", "args": {"host": "example.com"}},),
    targets=("example.com",),
)


def test_strict_fails_closed_to_quarantine():
    verdict = WatchdogClient(trust_level=TrustLevel.STRICT).gate(TRACE)
    assert verdict.verdict is Verdict.QUARANTINE
    assert verdict.rationale == "watchdog_unreachable_strict"


def test_permissive_fails_open_to_allow():
    verdict = WatchdogClient(trust_level=TrustLevel.PERMISSIVE).gate(TRACE)
    assert verdict.verdict is Verdict.ALLOW
    assert verdict.rationale == "watchdog_unreachable_permissive"


def test_gate_never_raises_and_emits_audit_event():
    verdict = WatchdogClient(trust_level=TrustLevel.STRICT).gate(TRACE)
    assert verdict.audit_event["vector_id"] == "recon"
    assert verdict.audit_event["action"] == "enumerate"
    assert "error" in verdict.audit_event
