# Base image
FROM python:3.10-slim

# System deps for building llama-cpp-python with OpenBLAS and for Pillow/TF
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       cmake \
       libopenblas-dev \
       libgomp1 \
       libgl1 \
       libglib2.0-0 \
       libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" \
    FORCE_CMAKE=1 \
    AI_SERVER_HOST=0.0.0.0 \
    AI_SERVER_PORT=8000 \
    DEBUG=false

WORKDIR /app

# Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Ensure models directory exists; mount real models at runtime via volume
RUN mkdir -p /app/models

EXPOSE 8000

# Optional model download at startup via environment variables
#   - KERAS_URL: HTTPS URL to DermaAI.keras
#   - GGUF_URL: HTTPS URL to tinyllama*.gguf
COPY ./scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Default command uses PORT if provided (e.g., Render), else AI_SERVER_PORT
ENTRYPOINT ["/entrypoint.sh"]
CMD ["sh", "-c", "gunicorn -w 1 -k gthread -t 180 -b 0.0.0.0:${PORT:-${AI_SERVER_PORT:-8000}} run_server:app"]


