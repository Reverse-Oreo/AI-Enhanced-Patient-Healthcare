# Multi-stage build for React frontend + Python backend
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY my-app/package*.json ./
RUN npm install
COPY my-app/ ./
RUN npm run build

FROM python:3.12-slim AS python-builder
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
ARG ENABLE_GPU=false
RUN if [ "$ENABLE_GPU" = "true" ]; then \
    pip install --no-cache-dir -r requirements.txt; \
    else \
    grep -v "llama-cpp-python\\\[cublas\\\]" requirements.txt > requirements_cpu.txt && \
    echo "llama-cpp-python" >> requirements_cpu.txt && \
    pip install --no-cache-dir -r requirements_cpu.txt; \
    fi

FROM python:3.12-slim
WORKDIR /app

# Copy only the installed packages, not build tools
COPY --from=python-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=python-builder /usr/local/bin /usr/local/bin

# Copy backend code
COPY backend/ ./

# Copy frontend build
COPY --from=frontend-build /app/frontend/build ./static

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]