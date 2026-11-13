import os
import threading
from flask import Flask, request, jsonify
app = Flask(__name__)
ready = False
error = None
installed = set()
lock = threading.Lock()

def setup():
    global ready, error, installed
    try:
        import argostranslate.package
        import argostranslate.translate
        argostranslate.package.update_package_index()
        available = argostranslate.package.get_available_packages()
        for src, dst in [('ko','en')]:
            match = next((p for p in available if p.from_code == src and p.to_code == dst), None)
            if match:
                argostranslate.package.install_from_path(match.download())
                installed.add((src,dst))
        ready = bool(installed)
        if not ready:
            error = 'ko-en model unavailable'
    except Exception as exc:
        error = str(exc)[:300]

@app.get('/health')
def health():
    return jsonify(status='ready' if ready else ('error' if error else 'loading'), pairs=[list(p) for p in sorted(installed)], error=error)

@app.post('/translate')
def translate():
    if not ready:
        return jsonify(error='translation_unavailable'), 503
    payload = request.get_json(silent=True) or {}
    text = payload.get('text')
    source = payload.get('source','ko')
    target = payload.get('target','en')
    if not isinstance(text,str) or not text.strip() or len(text)>500 or source not in ('ko','en','ja') or target not in ('ko','en','ja'):
        return jsonify(error='invalid_request'),400
    if source == target:
        return jsonify(translatedText=text)
    import argostranslate.translate
    try:
        with lock:
            result = argostranslate.translate.translate(text,source,target)
        return jsonify(translatedText=result)
    except Exception:
        return jsonify(error='translation_unavailable'),503

if __name__ == '__main__':
    threading.Thread(target=setup,daemon=True).start()
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT','10000')))
else:
    threading.Thread(target=setup,daemon=True).start()
