FROM python:3.11-slim

# Install GDAL + dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    binutils \
 && GDAL_SO=$(find /usr/lib/x86_64-linux-gnu -name "libgdal.so.*" | head -n 1) \
 && ln -s $GDAL_SO /usr/lib/libgdal.so \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
