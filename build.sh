#!/usr/bin/env bash
set -o errexit

apt-get update
apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    python3-dev \
    postgresql-client \
    build-essential


pip install --upgrade pip

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate