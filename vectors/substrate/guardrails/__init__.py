"""
vectors/substrate/guardrails — BugBountyOS Security Boundary Enforcement.

Security Operating System — Threat Boundary Enforcement Layer.

Exposes the pre-inference gate (InputScanner) and post-inference gate
(OutputValidator) used by the substrate processor to wrap all LLM
interactions with recon data.
"""

from .input_scanner import (
    InputScanner,
    ScanResult,
    ThreatLevel,
    apply_sandwich_defense,
    apply_structured_separation,
)
from .output_validator import (
    OutputValidator,
    PiiScanResult,
    ValidationResult,
    check_canary_token,
    detect_pii,
    detect_prompt_leakage,
)

__all__ = [
    "InputScanner",
    "ScanResult",
    "ThreatLevel",
    "apply_sandwich_defense",
    "apply_structured_separation",
    "OutputValidator",
    "PiiScanResult",
    "ValidationResult",
    "check_canary_token",
    "detect_pii",
    "detect_prompt_leakage",
]
