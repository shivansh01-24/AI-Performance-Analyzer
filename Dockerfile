# Ultra-small & fast image – ~120 MB final size
FROM python:3.10-slim

# Prevent Python buffering + create non-root user
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install only what we need
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

# Copy code
COPY . .

# Expose Dash port
EXPOSE 8050

# Run as non-root for security
USER 1000

# Start the app (Modular version)
CMD ["python", "main.py"]
