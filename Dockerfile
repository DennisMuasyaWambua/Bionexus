FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    binutils \
    && GDAL_SO=$(find /usr/lib/x86_64-linux-gnu -name "libgdal.so.*" | grep -v ".so.$" | head -n 1) \
    && if [ -n "$GDAL_SO" ]; then ln -sf "$GDAL_SO" /usr/lib/x86_64-linux-gnu/libgdal.so; else echo "GDAL .so not found"; fi \
    && rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
ENV GDAL_DATA=/usr/share/gdal
ENV PROJ_LIB=/usr/share/proj

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
