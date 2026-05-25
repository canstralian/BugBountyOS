from flask import jsonify
from app import app


@app.route("/api/health")
def health():
    """
    Provide a simple health-check JSON response for the /api/health endpoint.
    
    Returns:
        A Flask Response containing the JSON object {'status': 'ok'}.
    """
    return jsonify({"status": "ok"})
