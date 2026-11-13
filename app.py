import os
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request, jsonify

app = Flask(__name__)
SUPPORTED = {'ko', 'en', 'ja'}

def translate_text(value, source, target):
    if source not in SUPPORTED or target not in SUPPORTED or source == target:
        raise ValueError('unsupported_language_pair')
    if not isinstance(value, str) or not value.strip() or len(value) > 160 or len(value.encode('utf-8')) > 480:
        raise ValueError('invalid_text')
    # Anonymous free tier: no account, billing, or API key. Text is shared with MyMemory.
    params = urlencode({'q': value, 'langpair': source + '|' + target})
    req = Request('https://api.mymemory.translated.net/get?' + params,
                  headers={'User-Agent': 'TravelBookmark/1.0'})
    with urlopen(req, timeout=7) as response:
        data = json.load(response)
    if int(data.get('responseStatus', 0)) != 200:
        raise RuntimeError('free_provider_limit_or_error')
    result = data.get('responseData', {}).get('translatedText', '')
    if not isinstance(result, str) or not result.strip() or result.strip().lower() in ('no translation found', 'quota exceeded'):
        raise RuntimeError('translation_unavailable')
    return result

@app.get('/health')
def health():
    return jsonify(status='ready', mode='lightweight', translation='free_external', billing='free')

@app.get('/test')
def test_translation():
    try:
        translated = translate_text('부산 가족 여행', 'ko', 'en')
        return jsonify(status='ok', original='부산 가족 여행', translatedText=translated)
    except Exception as exc:
        return jsonify(status='error', reason=str(exc)[:100]), 503

@app.post('/translate')
def translate():
    data = request.get_json(silent=True) or {}
    try:
        result = translate_text(data.get('text'), data.get('source', 'ko'), data.get('target', 'en'))
        return jsonify(translatedText=result)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except Exception:
        return jsonify(error='translation_unavailable'), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '10000')))
