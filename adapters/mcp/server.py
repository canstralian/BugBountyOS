from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("BugBountyOS Kernel")

Verdict = Literal["allow", "deny", "quarantine", "human_review"]

_review_queue: dict[str, dict] = {}


@mcp.tool()
def check_scope(asset_id: str) -> str:
    """Query the BugBountyOS Immune System to verify if an asset is authorized."""
    return "Importing Airtable Adapter... Currently Permissive mode."


@mcp.tool()
def list_vectors() -> list:
    """Return the current state of the Vector Registry."""
    return ["dashboard", "pipeline", "storage", "red-sage", "cognition",
            "sensory", "recon", "substrate", "classifier"]


@mcp.tool()
def make_decision(vector: str, action: str, confidence: float = 1.0) -> dict:
    """
    Kernel policy decision endpoint.

    Returns one of: allow | deny | quarantine | human_review.
    human_review is issued when classifier confidence is below threshold.
    """
    CONFIDENCE_THRESHOLD = 0.75

    if confidence < CONFIDENCE_THRESHOLD:
        item_id = str(uuid.uuid4())
        _review_queue[item_id] = {
            "id": item_id,
            "vector": vector,
            "action": action,
            "confidence": confidence,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }
        return {"verdict": "human_review", "review_id": item_id}

    return {"verdict": "allow", "vector": vector, "action": action}


@mcp.tool()
def get_review_queue() -> list[dict]:
    """Return all pending human-review items."""
    return [item for item in _review_queue.values() if item["status"] == "pending"]


@mcp.tool()
def resolve_review(review_id: str, verdict: Verdict, operator: str = "unknown") -> dict:
    """
    Operator resolves a human_review item with allow or deny.
    Records the decision in the audit trail.
    """
    if review_id not in _review_queue:
        return {"error": f"review_id {review_id!r} not found"}
    if verdict not in ("allow", "deny"):
        return {"error": "verdict must be 'allow' or 'deny'"}

    _review_queue[review_id]["status"] = "resolved"
    _review_queue[review_id]["verdict"] = verdict
    _review_queue[review_id]["resolved_by"] = operator
    _review_queue[review_id]["resolved_at"] = datetime.now(timezone.utc).isoformat()

    return {"verdict": verdict, "review_id": review_id, "resolved_by": operator}


if __name__ == "__main__":
    mcp.run(transport="stdio")
