from app import db
class BugReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_text = db.Column(db.Text, nullable=False)
from datetime import datetime, timezone


class ReconEvent:
    """In-memory representation of an inbound reconnaissance event (not persisted here)."""

    def __init__(self, target: str, findings: list, timestamp: str = ""):
        self.target = target
        self.findings = findings
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    def validate(self) -> list[str]:
        errors = []
        if not self.target:
            errors.append("target is required")
        if not isinstance(self.findings, list):
            errors.append("findings must be an array")
        return errors

