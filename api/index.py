from app import app
from flask import request, jsonify

def handler(request):
    if request.method == 'POST':
        try:
            update = request.get_json()
            app.process_update(update)
            return jsonify({'status': 'ok'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    return jsonify({'status': 'error', 'message': 'Method not allowed'}), 405 