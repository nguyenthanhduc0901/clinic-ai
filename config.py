import os
from dotenv import load_dotenv


class Config:
    DEBUG = True
    HOST = os.environ.get("AI_SERVER_HOST", "0.0.0.0")
    PORT = int(os.environ.get("AI_SERVER_PORT", "8000"))

    # Vision model (TensorFlow Keras) local filename in ai_server/models
    HF_MODEL_FILE = os.environ.get("VISION_KERAS_FILE", "DermaAI.keras")

    # Text model (llama.cpp GGUF) in local folder ai_server/models
    PREFERRED_GGUF = [
        "tinyllama-1.1b-chat-v1.0.Q8_0.gguf"
    ]
    MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

    # ASR (speech-to-text)
    # Load .env (if present)
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

    ASR_PROVIDER = os.environ.get("ASR_PROVIDER", "openai").lower()  # openai | deepgram
    ASR_API_KEY = os.environ.get("ASR_API_KEY", "")
    ASR_MODEL = os.environ.get("ASR_MODEL", "whisper-1")  # used for OpenAI
    ASR_TIMEOUT = int(os.environ.get("ASR_TIMEOUT", "600"))
    ALLOWED_AUDIO_MIME_TYPES = {
        "audio/webm",
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",      # mp3
        "audio/mp3",
        "audio/m4a",
        "audio/mp4",
        "audio/ogg",
        "application/octet-stream",  # fallback
    }


