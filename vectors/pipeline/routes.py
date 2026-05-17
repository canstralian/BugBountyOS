from flask import Flask, request, jsonify
from nlp_processor import NLPProcessor


def register_routes(app: Flask):
    processor = NLPProcessor(provider=app.config.get("NLP_PROVIDER"))

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "vector": "pipeline", "provider": processor.provider})

    @app.route("/api/events", methods=["POST"])
    def ingest_event():
        body = request.get_json(silent=True)
        if not body:
            return jsonify({"error": "JSON body required"}), 400

        target = body.get("target")
        findings = body.get("findings", [])
        if not target:
            return jsonify({"error": "'target' is required"}), 422
        if not isinstance(findings, list):
            return jsonify({"error": "'findings' must be an array"}), 422

        action_plan = processor.process(target, findings)
        return jsonify(action_plan), 201
