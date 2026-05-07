from flask import jsonify
from app import app
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})