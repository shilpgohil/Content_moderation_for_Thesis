# Use Python 3.10 slim image for smaller size
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set cache directories to persist in the Docker image
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV HF_HOME=/app/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence_transformers

# Install system dependencies required for compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create cache directories
RUN mkdir -p /app/.cache/huggingface /app/.cache/sentence_transformers

# Copy requirements file
COPY requirements.txt .

# CRITICAL: Install CPU-only PyTorch first to save space (approx 2GB saved)
# This prevents installing the massive CUDA version
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model as a pip package (more reliable than spacy download command)
RUN pip install --no-cache-dir https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Link the model (ensures spacy.load("en_core_web_sm") works)
RUN python -m spacy link en_core_web_sm en_core_web_sm

# Verify spaCy model is installed correctly
RUN python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy model verified!')"

# Pre-download SentenceTransformer model to the explicit cache directory
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2'); print('SentenceTransformer model verified!')"

# Copy the application code
COPY . .

# Expose the port (Render handles this dynamically but good for documentation)
EXPOSE 8000

# Run the application with dynamic PORT
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
