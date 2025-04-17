from app import app
from flask import request, jsonify

def handler(request):
    if request.method == 'POST':
        update = request.get_json()
        app.process_update(update)
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error', 'message': 'Method not allowed'}), 405 