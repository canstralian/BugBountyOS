"""Adrian watchdog adapter — kernel-side call site for the reasoning-trace gate."""

from .watchdog_client import (
    BlockSignal,
    ReasoningTrace,
    TrustLevel,
    Verdict,
    WatchdogClient,
    WatchdogUnavailable,
    WatchdogVerdict,
)

__all__ = [
    "BlockSignal",
    "ReasoningTrace",
    "TrustLevel",
    "Verdict",
    "WatchdogClient",
    "WatchdogUnavailable",
    "WatchdogVerdict",
]
