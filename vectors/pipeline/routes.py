from app import app
from flask import jsonify


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})
