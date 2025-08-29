from flask import Blueprint, request, jsonify

from services.text_service import MedicalDialogueAnalyzer
from services.asr_service import ASRService
from config import Config


bp = Blueprint("text", __name__)
bp_alias = Blueprint("text_alias", __name__)
_analyzer: MedicalDialogueAnalyzer | None = None
_asr: ASRService | None = None


def get_analyzer() -> MedicalDialogueAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = MedicalDialogueAnalyzer()
    return _analyzer


def get_asr() -> ASRService:
    global _asr
    if _asr is None:
        _asr = ASRService()
    return _asr


@bp.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json(silent=True) or {}
        text = data.get('text')
        texts = data.get('texts')

        has_text = isinstance(text, str) and text.strip() != ''
        has_texts = isinstance(texts, list) and len(texts) > 0

        if not has_text and not has_texts:
            return jsonify({'error': "Provide 'text' (string) or 'texts' (list of strings)."}), 400
        if has_text and has_texts:
            return jsonify({'error': "Provide either 'text' or 'texts', not both."}), 400

        analyzer = get_analyzer()

        if has_text:
            result = analyzer.analyze(text)
            return jsonify(result)

        cleaned = [t for t in texts if isinstance(t, str) and t.strip() != '']
        if not cleaned:
            return jsonify({'error': "'texts' must contain at least one non-empty string."}), 400

        results = [analyzer.analyze(t) for t in cleaned]
        return jsonify({'results': results})

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
def _validate_audio(file_storage) -> tuple[bytes, str]:
    if file_storage is None:
        raise ValueError("Missing 'file'")
    mime = file_storage.mimetype or "application/octet-stream"
    allowed = Config.ALLOWED_AUDIO_MIME_TYPES
    if mime not in allowed:
        raise ValueError("Unsupported media type")
    data = file_storage.read()
    if not data:
        raise ValueError("Empty audio")
    return data, mime


@bp.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'file' not in request.files:
            return jsonify({'error': "missing 'file'"}), 400
        file_bytes, mime = _validate_audio(request.files.get('file'))
        language = request.form.get('language', 'vi')
        transcript = get_asr().transcribe(file_bytes, mime, language=language)
        if not transcript:
            return jsonify({'error': 'transcription failed'}), 500
        return jsonify({'transcript': transcript})
    except ValueError as ve:
        status = 415 if str(ve) == "Unsupported media type" else 400
        return jsonify({'error': str(ve)}), status
    except RuntimeError as re:
        return jsonify({'error': str(re)}), 500
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@bp.route('/transcribe-and-analyze', methods=['POST'])
def transcribe_and_analyze():
    try:
        if 'file' not in request.files:
            return jsonify({'error': "missing 'file'"}), 400
        file_bytes, mime = _validate_audio(request.files.get('file'))
        language = request.form.get('language', 'vi')
        transcript = get_asr().transcribe(file_bytes, mime, language=language)
        if not transcript:
            return jsonify({'error': 'transcription failed'}), 500
        ai_result = get_analyzer().analyze(transcript)
        return jsonify({'transcript': transcript, 'ai': ai_result})
    except ValueError as ve:
        status = 415 if str(ve) == "Unsupported media type" else 400
        return jsonify({'error': str(ve)}), status
    except RuntimeError as re:
        return jsonify({'error': str(re)}), 500
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


# Aliases under /ai/text/...
@bp_alias.route('/transcribe', methods=['POST'])
def transcribe_alias():
    return transcribe()


@bp_alias.route('/transcribe-and-analyze', methods=['POST'])
def transcribe_and_analyze_alias():
    return transcribe_and_analyze()



