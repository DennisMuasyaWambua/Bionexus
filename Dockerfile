FROM python:3.11-slim

# Install required packages including GDAL
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    python3-gdal \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create .env file for Docker build
RUN echo "DEBUG=False" > .env && \
    echo "SECRET_KEY=docker-build-key" >> .env && \
    echo "USE_SQLITE=True" >> .env && \
    echo "ALLOWED_HOSTS=*" >> .env

# Collect static files (using SQLite config from .env)
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD gunicorn bionexus_gaia.wsgi:application