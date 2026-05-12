from flask import jsonify

from vectors.pipeline.app import app


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})
