from flask import Blueprint, request, jsonify

from services.text_service import MedicalDialogueAnalyzer


bp = Blueprint("text", __name__)
_analyzer: MedicalDialogueAnalyzer | None = None


def get_analyzer() -> MedicalDialogueAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = MedicalDialogueAnalyzer()
    return _analyzer


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
