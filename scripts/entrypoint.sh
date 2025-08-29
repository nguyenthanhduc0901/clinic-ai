#!/usr/bin/env sh
set -e

MODEL_DIR="/app/models"
mkdir -p "$MODEL_DIR"

# Download Keras model if KERAS_URL is set and file not present
if [ -n "$KERAS_URL" ]; then
  DEST_KERAS="$MODEL_DIR/DermaAI.keras"
  if [ ! -f "$DEST_KERAS" ]; then
    echo "Downloading Keras model from $KERAS_URL ..."
    curl -fsSL "$KERAS_URL" -o "$DEST_KERAS"
  fi
fi

# Download GGUF model if GGUF_URL is set and file not present
if [ -n "$GGUF_URL" ]; then
  # Keep original filename from URL if possible
  FNAME=$(basename "$GGUF_URL")
  DEST_GGUF="$MODEL_DIR/$FNAME"
  if [ ! -f "$DEST_GGUF" ]; then
    echo "Downloading GGUF model from $GGUF_URL ..."
    curl -fsSL "$GGUF_URL" -o "$DEST_GGUF"
  fi
fi

exec "$@"


