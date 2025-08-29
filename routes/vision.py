from flask import Blueprint, request, jsonify

from services.vision_service import VisionClassifier


bp = Blueprint("vision", __name__)
_classifier: VisionClassifier | None = None


def get_classifier() -> VisionClassifier:
    global _classifier
    if _classifier is None:
        _classifier = VisionClassifier()
    return _classifier


@bp.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(silent=True) or {}
        image_b64 = data.get('image')
        if not isinstance(image_b64, str) or not image_b64.strip():
            return jsonify({'error': "'image' (base64 string) is required"}), 400

        classifier = get_classifier()
        result = classifier.predict(image_b64)
        return jsonify(result)

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


