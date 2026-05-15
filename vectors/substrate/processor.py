"""
vectors/substrate/processor.py — BugBountyOS Substrate Processor.

Security Operating System — Core Recon Processing Engine.

All externally-sourced recon data passes through this processor before it
reaches the reasoning layer and before any analysis output is surfaced to
operators or downstream vectors.

Three-layer defense model enforced on every cycle:

  Pre-Inference Gate  → InputScanner scans for injection / high-entropy payloads.
  Sandwich Defense    → Structured separation + reinforcement wrapping prevents
                        latent directives from hijacking the model's context.
  Post-Inference Gate → OutputValidator checks for canary exfiltration, system
                        prompt leakage, and PII before output is released.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from .guardrails import (
    InputScanner,
    OutputValidator,
    ScanResult,
    ThreatLevel,
    ValidationResult,
    apply_sandwich_defense,
    apply_structured_separation,
)

logger = logging.getLogger(__name__)


class ReconSecurityViolation(Exception):
    """Raised when the pre-inference gate blocks a recon payload."""


class ReconOutputViolation(Exception):
    """Raised when the post-inference gate blocks an analysis output."""


@dataclass
class ProcessorConfig:
    """Runtime configuration for the substrate processor security gates."""
    canary_token: Optional[str] = None
    redact_pii: bool = True
    block_on_pii: bool = False
    max_input_length: int = 50_000
    entropy_threshold: float = 5.5
    strict_mode: bool = True
    sandwich_reinforcement: Optional[str] = None


@dataclass
class ProcessingResult:
    """Structured outcome returned to callers after a full processing cycle."""
    success: bool
    output: str
    scan_result: Optional[ScanResult] = None
    validation_result: Optional[ValidationResult] = None
    blocked_at: Optional[str] = None
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class SubstrateProcessor:
    """
    BugBountyOS Substrate Processor — Security-hardened recon analysis engine.

    Wraps every LLM call with:
      1. Pre-inference gate  — rejects injected / malformed inputs fail-closed.
      2. Sandwich Defense    — neutralises latent directives in recon payloads.
      3. Post-inference gate — blocks leaked system prompts, canary exfiltration,
                               and PII before output reaches the operator surface.

    Usage::

        processor = SubstrateProcessor(config=ProcessorConfig(canary_token="BBOS-..."))

        result = processor.process(
            raw_recon_data="<externally sourced recon payload>",
            inference_fn=my_llm_call,
        )

        if not result.success:
            logger.warning("[BBOS] Processing blocked at %s: %s", result.blocked_at, result.reason)
        else:
            operator_surface(result.output)
    """

    def __init__(self, config: Optional[ProcessorConfig] = None) -> None:
        self.config = config or ProcessorConfig()
        self._scanner = InputScanner(
            max_length=self.config.max_input_length,
            entropy_threshold=self.config.entropy_threshold,
            strict_mode=self.config.strict_mode,
        )
        self._validator = OutputValidator(
            canary_token=self.config.canary_token,
            redact_pii=self.config.redact_pii,
            block_on_pii=self.config.block_on_pii,
        )

    def _pre_inference_gate(self, raw_input: str) -> ScanResult:
        """
        Pre-inference gate: scan for injection patterns and high-entropy payloads.

        Returns a ScanResult. Callers should fail-closed on result.passed == False.
        """
        result = self._scanner.scan(raw_input)
        if not result.passed:
            logger.warning(
                "[BBOS][PRE-GATE] Input blocked — threat_level=%s reason=%s threats=%s",
                result.threat_level,
                result.reason,
                result.threats,
            )
        elif result.threats:
            logger.info(
                "[BBOS][PRE-GATE] Input passed with warnings — %s",
                result.threats,
            )
        return result

    def _apply_sandwich(self, sanitized_input: str) -> str:
        """
        Sandwich Defense: wrap sanitized recon data in structured separation
        + a trailing reinforcement footer.
        """
        wrapped = apply_structured_separation(sanitized_input)
        sandwiched = apply_sandwich_defense(
            wrapped,
            reinforcement=self.config.sandwich_reinforcement,
        )
        return sandwiched

    def _post_inference_gate(self, raw_output: str) -> ValidationResult:
        """
        Post-inference gate: validate LLM output for canary tokens, prompt
        leakage, and PII before surfacing to operators.

        Returns a ValidationResult. Callers should fail-closed on result.passed == False.
        """
        result = self._validator.validate(raw_output)
        if not result.passed:
            logger.warning(
                "[BBOS][POST-GATE] Output blocked — failures=%s reasons=%s",
                result.blocking_failures,
                result.reasons,
            )
        elif result.pii_types:
            logger.info(
                "[BBOS][POST-GATE] Output passed with PII redacted — types=%s",
                result.pii_types,
            )
        return result

    def process(
        self,
        raw_recon_data: str,
        inference_fn: Callable[[str], str],
    ) -> ProcessingResult:
        """
        Execute a full security-hardened recon analysis cycle.

        Args:
            raw_recon_data: Externally-sourced recon payload (untrusted).
            inference_fn:   Callable that accepts the secured prompt and returns
                            the raw LLM analysis string.

        Returns:
            ProcessingResult with success=True and validated output,
            or success=False with blocked_at and reason populated.
        """
        scan = self._pre_inference_gate(raw_recon_data)
        if not scan.passed:
            return ProcessingResult(
                success=False,
                output="",
                scan_result=scan,
                blocked_at="pre_inference_gate",
                reason=scan.reason,
                metadata={"threats": scan.threats, "threat_level": scan.threat_level},
            )

        secured_prompt = self._apply_sandwich(scan.sanitized)

        try:
            raw_output = inference_fn(secured_prompt)
        except Exception as exc:
            logger.error("[BBOS][SUBSTRATE] Inference call failed: %s", exc)
            return ProcessingResult(
                success=False,
                output="",
                scan_result=scan,
                blocked_at="inference",
                reason=f"Inference call raised exception: {exc}",
            )

        validation = self._post_inference_gate(raw_output)
        if not validation.passed:
            return ProcessingResult(
                success=False,
                output="",
                scan_result=scan,
                validation_result=validation,
                blocked_at="post_inference_gate",
                reason="; ".join(validation.reasons.get(k, "") for k in validation.blocking_failures),
                metadata={"blocking_failures": validation.blocking_failures},
            )

        return ProcessingResult(
            success=True,
            output=validation.output,
            scan_result=scan,
            validation_result=validation,
            reason="OK",
            metadata={
                "pii_redacted": validation.pii_types,
                "input_threats": scan.threats,
            },
        )
