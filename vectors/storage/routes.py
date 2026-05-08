from flask import Flask, request, jsonify
from app import db
from models import Finding, Evidence, ToolRun


def register_routes(app: Flask):

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "vector": "storage"})

    # --- Findings (append-only) ---

    @app.route("/api/findings", methods=["GET"])
    def list_findings():
        findings = Finding.query.order_by(Finding.created_at.desc()).all()
        return jsonify([f.to_dict() for f in findings])

    @app.route("/api/findings/<int:finding_id>", methods=["GET"])
    def get_finding(finding_id):
        finding = Finding.query.get_or_404(finding_id)
        return jsonify(finding.to_dict())

    @app.route("/api/findings", methods=["POST"])
    def create_finding():
        body = request.get_json(silent=True)
        if not body:
            return jsonify({"error": "JSON body required"}), 400
        required = ("target", "severity", "title", "description")
        missing = [f for f in required if not body.get(f)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 422

        finding = Finding(
            target=body["target"],
            severity=body["severity"],
            title=body["title"],
            description=body["description"],
            status=body.get("status", "draft"),
            source_action_plan_id=body.get("source_action_plan_id"),
        )
        db.session.add(finding)
        db.session.commit()
        return jsonify(finding.to_dict()), 201

    # --- Evidence (append-only) ---

    @app.route("/api/evidence", methods=["GET"])
    def list_evidence():
        evidence = Evidence.query.order_by(Evidence.created_at.desc()).all()
        return jsonify([e.to_dict() for e in evidence])

    @app.route("/api/evidence", methods=["POST"])
    def create_evidence():
        body = request.get_json(silent=True)
        if not body:
            return jsonify({"error": "JSON body required"}), 400
        if not body.get("kind") or not body.get("value"):
            return jsonify({"error": "Missing required fields: kind, value"}), 422

        evidence = Evidence(
            finding_id=body.get("finding_id"),
            kind=body["kind"],
            value=body["value"],
            sha256=body.get("sha256"),
        )
        db.session.add(evidence)
        db.session.commit()
        return jsonify(evidence.to_dict()), 201

    # --- Tool runs (append-only) ---

    @app.route("/api/tool-runs", methods=["GET"])
    def list_tool_runs():
        runs = ToolRun.query.order_by(ToolRun.created_at.desc()).all()
        return jsonify([r.to_dict() for r in runs])

    @app.route("/api/tool-runs", methods=["POST"])
    def create_tool_run():
        body = request.get_json(silent=True)
        if not body:
            return jsonify({"error": "JSON body required"}), 400
        if not body.get("tool") or not body.get("target"):
            return jsonify({"error": "Missing required fields: tool, target"}), 422

        run = ToolRun(
            tool=body["tool"],
            target=body["target"],
            status=body.get("status", "running"),
            output_ref=body.get("output_ref"),
        )
        db.session.add(run)
        db.session.commit()
        return jsonify(run.to_dict()), 201
