import os
from flask import Flask, request, jsonify
app = Flask(__name__)

# Models are installed at image build time, not downloaded on every cold start.
# Translation loading is lazy so health checks do not allocate model memory.
@app.get('/health')
def health():
    import pathlib
    model_dir = pathlib.Path('/root/.local/share/argos-translate/packages')
    packages = [p.name for p in model_dir.glob('*') if p.is_dir()] if model_dir.exists() else []
    return jsonify(status='ready' if packages else 'no_model', packages=packages)

@app.get('/test')
def test_translation():
    try:
        import argostranslate.translate
        source_text = '부산 가족 여행'
        result = argostranslate.translate.translate(source_text, 'ko', 'en')
        return jsonify(status='ok', original=source_text, translatedText=result)
    except Exception as exc:
        return jsonify(status='error', error=str(exc)[:180]),503

@app.post('/translate')
def translate():
    data = request.get_json(silent=True) or {}
    value, source, target = data.get('text'), data.get('source','ko'), data.get('target','en')
    if not isinstance(value,str) or not value.strip() or len(value)>300 or (source,target)!=('ko','en'):
        return jsonify(error='unsupported_translation'),400
    try:
        import argostranslate.translate
        result = argostranslate.translate.translate(value,source,target)
        return jsonify(translatedText=result)
    except Exception as exc:
        return jsonify(error='translation_failed',detail=str(exc)[:100]),503

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT','10000')))
