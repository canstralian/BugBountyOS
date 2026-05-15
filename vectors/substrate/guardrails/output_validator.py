"""
vectors/substrate/guardrails/output_validator.py — LLM Output Validation Pipeline.

Ported from canstralian/DarkOsint (branch: claude/guardrail-integration)
src/guardrails/output_validator.py and adapted to BugBountyOS substrate conventions.

Security Operating System — Post-Inference Gate.

Fail-closed: if validation fails the output is NOT surfaced to the caller.

Pipeline:
  1. Canary token check   — detects prompt extraction attacks
  2. Prompt leakage check — system instruction bleed-through
  3. PII detection        — SSN, credit card, email, phone, address
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


_PII_PATTERNS: List[tuple[re.Pattern, str]] = [
    (re.compile(r"\b\d{3}[-.}?\d{2}[-.]?\d{4}\b"), "ssn"),
    (re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"), "credit_card"),
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), "email"),
    (re.compile(
        r"\b(?:\+?\d{1,3}[\-.\s]?)?\(?\d{3}\)?[\-.\s]?\d{3}[\-.\s]?\d{4}\b"
    ), "phone"),
    (re.compile(
        r"\b\d{1,5}\s+[\w\s]+(?:street|st|avenue|ave|road|rd|boulevard|blvd|"
        r"drive|dr|lane|ln|way|court|ct)\b",
        re.IGNORECASE,
    ), "address"),
]

_LEAKAGE_PATTERNS: List[tuple[re.Pattern, str]] = [
    (re.compile(r"##\s*ROLE\n", re.IGNORECASE), "role_leak"),
    (re.compile(r"##\s*OBJECTIVE\n", re.IGNORECASE), "objective_leak"),
    (re.compile(r"##\s*CONSTRAINTS\n", re.IGNORECASE), "constraints_leak"),
    (re.compile(r"##\s*OUTPUT\s*(FORMAT|SHAPE)\n", re.IGNORECASE), "output_shape_leak"),
    (re.compile(r"system\s*prompt\s*:", re.IGNORECASE), "system_prompt_leak"),
    (re.compile(r"my\s+instructions?\s+(are|say|tell)", re.IGNORECASE), "instruction_leak"),
    (re.compile(r"##\s*Core\s+Competencies", re.IGNORECASE), "system_prompt_leak"),
    (re.compile(r"##\s*Legal\s*&?\s*Ethical\s+Framework", re.IGNORECASE), "system_prompt_leak"),
    (re.compile(r"##\s*Intelligence\s+Reporting\s+Standards", re.IGNORECASE), "system_prompt_leak"),
    (re.compile(r"##\s*Scope\s+Rules", re.IGNORECASE), "system_prompt_leak"),
    (re.compile(r"##\s*Bug\s*Bounty\s*OS\s*Kernel", re.IGNORECASE), "system_prompt_leak"),
]


@dataclass
class PiiScanResult:
    detected_types: List[str] = field(default_factory=list)
    redacted: str = ""

    @property
    def has_pii(self) -> bool:
        return bool(self.detected_types)


@dataclass
class ValidationResult:
    passed: bool
    output: str
    verdicts: Dict[str, bool] = field(default_factory=dict)
    reasons: Dict[str, str] = field(default_factory=dict)
    pii_types: List[str] = field(default_factory=list)

    @property
    def blocking_failures(self) -> List[str]:
        return [k for k, v in self.verdicts.items() if not v]


def check_canary_token(output: str, canary: str) -> tuple[bool, str]:
    """Return (passed, reason). Fails if the canary appears verbatim in output."""
    if canary and canary in output:
        return False, "Canary token detected in output — prompt extraction attack intercepted by BBOS guardrail"
    return True, "Canary token not present"


def detect_pii(output: str, redact: bool = True) -> PiiScanResult:
    detected_types: list[str] = []
    redacted = output
    for pattern, label in _PII_PATTERNS:
        if pattern.search(output):
            detected_types.append(label)
            if redact:
                redacted = pattern.sub(f"[REDACTED:{label}]", redacted)
    return PiiScanResult(detected_types=detected_types, redacted=redacted)


def detect_prompt_leakage(output: str) -> tuple[bool, str, List[str]]:
    """Return (passed, reason, list_of_leak_labels)."""
    leaks: list[str] = []
    for pattern, label in _LEAKAGE_PATTERNS:
        if pattern.search(output):
            leaks.append(label)
    if leaks:
        return False, f"Prompt leakage detected: {', '.join(leaks)}", leaks
    return True, "No leakage detected", []


class OutputValidator:
    """
    Post-inference output validation pipeline for the BugBountyOS substrate.

    Enforces the post-inference gate: all LLM-generated recon analysis passes
    through canary verification, leakage detection, and PII redaction before
    being surfaced to operators or downstream vectors.

    Usage::

        validator = OutputValidator(canary_token="BBOS-CANARY-<uuid>")
        result = validator.validate(llm_output)
        if not result.passed:
            # Fail-closed — quarantine output, surface security event.
            raise ReconOutputViolation(result.reasons)
        return result.output  # Possibly PII-redacted
    """

    def __init__(
        self,
        canary_token: Optional[str] = None,
        redact_pii: bool = True,
        block_on_pii: bool = False,
    ) -> None:
        self.canary_token = canary_token
        self.redact_pii = redact_pii
        self.block_on_pii = block_on_pii

    def validate(self, output: str) -> ValidationResult:
        verdicts: dict[str, bool] = {}
        reasons: dict[str, str] = {}
        current = output

        if self.canary_token:
            passed, reason = check_canary_token(current, self.canary_token)
            verdicts["canary"] = passed
            reasons["canary"] = reason
            if not passed:
                return ValidationResult(
                    passed=False,
                    output="",
                    verdicts=verdicts,
                    reasons=reasons,
                )

        passed, reason, _ = detect_prompt_leakage(current)
        verdicts["leakage"] = passed
        reasons["leakage"] = reason
        if not passed:
            return ValidationResult(
                passed=False,
                output="",
                verdicts=verdicts,
                reasons=reasons,
            )

        pii_result = detect_pii(current, redact=self.redact_pii)
        verdicts["pii"] = not pii_result.has_pii
        reasons["pii"] = (
            f"PII detected: {', '.join(pii_result.detected_types)}"
            if pii_result.has_pii
            else "No PII detected"
        )
        if self.redact_pii and pii_result.has_pii:
            current = pii_result.redacted

        if self.block_on_pii and pii_result.has_pii:
            return ValidationResult(
                passed=False,
                output="",
                verdicts=verdicts,
                reasons=reasons,
                pii_types=pii_result.detected_types,
            )

        blocking_keys = {"canary", "leakage"}
        all_passed = all(verdicts[k] for k in blocking_keys if k in verdicts)
        return ValidationResult(
            passed=all_passed,
            output=current,
            verdicts=verdicts,
            reasons=reasons,
            pii_types=pii_result.detected_types,
        )
