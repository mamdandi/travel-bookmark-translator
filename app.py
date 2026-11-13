import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get('/health')
def health():
    return jsonify(status='ready', mode='lightweight', translation='disabled', billing='free')

@app.get('/test')
def test_translation():
    return jsonify(status='disabled', reason='heavy_model_removed_to_fit_free_memory'), 503

@app.post('/translate')
def translate():
    # Fail closed until a verified no-cost translation provider is integrated.
    # No external calls, no user data forwarding, no paid APIs.
    return jsonify(error='translation_unavailable', reason='free_provider_not_configured'), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '10000')))
