from __future__ import annotations

from typing import Optional

from ..config import Config


class ASRService:
    """Minimal ASR service stub.

    In production, implement providers (e.g., OpenAI, Deepgram) here.
    For now, this raises if not configured so routes can fail gracefully.
    """

    def __init__(self) -> None:
        self.provider: str = Config.ASR_PROVIDER
        self.api_key: str = Config.ASR_API_KEY
        self.model: str = Config.ASR_MODEL
        self.timeout_seconds: int = Config.ASR_TIMEOUT

    def transcribe(self, audio_bytes: bytes, mime: str, *, language: str = "vi") -> str:
        if not self.api_key:
            raise RuntimeError("ASR not configured: missing ASR_API_KEY")
        raise NotImplementedError("ASR provider not implemented. Set up ASR integration.")


