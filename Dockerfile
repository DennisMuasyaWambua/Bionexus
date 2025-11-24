# ========================
#  Builder stage
# ========================
FROM python:3.11-slim AS builder

# Install system build dependencies (removed in final image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgdal-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ========================
#  Runtime stage
# ========================
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r django && useradd -r -g django django

# Install runtime-only dependencies (lighter than builder stage)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgdal-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Ensure GDAL is discoverable
# Ensure GDAL is discoverable
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu

# Add symlink so anything expecting /usr/lib/libgdal.so also works
RUN ln -s /usr/lib/x86_64-linux-gnu/libgdal.so /usr/lib/libgdal.so


# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy app code
COPY . .

# Static + media directories
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R django:django /app

# Switch user
USER django

# Collect static files
RUN python manage.py collectstatic --noinput

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# Django settings
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=bionexus_gaia.settings

# Health check
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD python -c "import requests; requests.get('http://localhost:8080/api/v1/auth/register/', timeout=10)"

# Expose port
EXPOSE 8080

# Set entrypoint and command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "bionexus_gaia.wsgi:application"]
