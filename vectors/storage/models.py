from datetime import datetime, timezone
from app import db


class Finding(db.Model):
    __tablename__ = "findings"

    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.String(512), nullable=False)
    severity = db.Column(db.String(16), nullable=False)  # critical|high|medium|low|info
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(32), nullable=False, default="draft")
    source_action_plan_id = db.Column(db.String(36))  # uuid from pipeline output
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "target": self.target,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "source_action_plan_id": self.source_action_plan_id,
            "created_at": self.created_at.isoformat(),
        }


class Evidence(db.Model):
    __tablename__ = "evidence"

    id = db.Column(db.Integer, primary_key=True)
    finding_id = db.Column(db.Integer, db.ForeignKey("findings.id"), nullable=True)
    kind = db.Column(db.String(64), nullable=False)  # screenshot|request|response|log
    value = db.Column(db.Text, nullable=False)
    sha256 = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "finding_id": self.finding_id,
            "kind": self.kind,
            "value": self.value,
            "sha256": self.sha256,
            "created_at": self.created_at.isoformat(),
        }


class ToolRun(db.Model):
    __tablename__ = "tool_runs"

    id = db.Column(db.Integer, primary_key=True)
    tool = db.Column(db.String(128), nullable=False)
    target = db.Column(db.String(512), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="running")
    output_ref = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "tool": self.tool,
            "target": self.target,
            "status": self.status,
            "output_ref": self.output_ref,
            "created_at": self.created_at.isoformat(),
        }
