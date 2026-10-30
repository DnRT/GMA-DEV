# ==============================================================================
# OpsSentinel - Secure Multi-Stage Dockerfile
# Compliant with CIS Docker Benchmark & Chilean Ley 21.663 (Non-root execution)
# ==============================================================================

# Stage 1: Build & Dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Minimal Distroless / Hardened Runtime
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install curl for container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Security: Create non-root system user and group (Ley 21.663 compliance)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -d /app appuser

# Copy installed dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Prepare app directories and permissions
RUN mkdir -p /app/audit_logs && \
    chown -R appuser:appgroup /app

# Copy application source code
COPY --chown=appuser:appgroup src/ /app/src/

# Switch to unprivileged user
USER appuser

# Expose HTTP port
EXPOSE 8080

# Healthcheck probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

# Launch production server
CMD ["python", "-m", "src.main"]
