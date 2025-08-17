FROM python:3.11-slim

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 bot

# Copy the requirements file
COPY --chown=bot:bot requirements.txt .

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project and set permissions
COPY --chown=bot:bot . .

# Create log directory and set permissions
RUN mkdir -p /app/logs && chown -R bot:bot /app/logs

# Switch to non-root user
USER bot

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PROMETHEUS_PORT}/metrics || exit 1

# Command to run the bot
CMD ["python", "main.py"]