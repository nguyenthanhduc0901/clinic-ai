import base64
import io
import os
from typing import List, Dict

import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras.applications.efficientnet_v2 import preprocess_input

from ..config import Config


class VisionClassifier:
    def __init__(self) -> None:
        model_path = os.path.join(Config.MODELS_DIR, Config.HF_MODEL_FILE)
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Keras model not found at {model_path}. Place the file in ai_server/models/")
        self.model = tf.keras.models.load_model(model_path)
        self.class_names = [
            'Atopic Dermatitis',
            'Eczema',
            'Psoriasis',
            'Seborrheic Keratoses',
            'Tinea Ringworm Candidiasis'
        ]

    def _prepare_image(self, image_b64: str) -> np.ndarray:
        if 'base64,' in image_b64:
            image_b64 = image_b64.split('base64,', 1)[1]
        decoded = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(decoded)).convert('RGB')
        image = image.resize((224, 224))
        arr = np.array(image)
        arr = preprocess_input(arr)
        arr = np.expand_dims(arr, axis=0)
        return arr

    def predict(self, image_b64: str) -> Dict:
        image_array = self._prepare_image(image_b64)
        predictions = self.model.predict(image_array)
        best_index = int(np.argmax(predictions[0]))
        best_label = self.class_names[best_index]
        best_conf = float(predictions[0][best_index] * 100)

        top_indices = np.argsort(predictions[0])[-3:][::-1]
        top_predictions: List[Dict] = []
        for idx in top_indices:
            if int(idx) == best_index:
                continue
            top_predictions.append({
                'class': self.class_names[int(idx)],
                'confidence': float(predictions[0][int(idx)] * 100)
            })

        if best_conf < 10:
            recommendation = "Very low confidence. Please retake image with better lighting and focus."
        elif best_conf < 30:
            recommendation = "Low confidence. Preliminary result only. Consult a dermatologist."
        elif best_conf < 60:
            recommendation = "Moderate confidence. Consider alternatives and consult healthcare professional."
        else:
            recommendation = "High confidence prediction. Always consult healthcare professional for confirmation."

        return {
            'prediction': best_label,
            'confidence': round(best_conf, 2),
            'all_confidences': {
                self.class_names[i]: float(pred * 100) for i, pred in enumerate(predictions[0])
            },
            'top_alternatives': top_predictions,
            'recommendation': recommendation
        }


