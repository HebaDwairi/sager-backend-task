# Use a specific Python base image with a slim OS version (Debian Bookworm)
FROM python:3.13-slim-bookworm

# Set environment variables for Python to prevent buffering and .pyc files
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install system dependencies for GeoDjango (GDAL, GEOS) and other build tools
# build-essential for compiling C extensions (like psycopg2-binary)
# libgdal-dev, libgeos-dev for GeoDjango's C libraries
# python3-dev for Python header files needed for some pip packages
# postgresql-client (optional) if you want psql command inside the container
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    libgeos-dev \
    python3-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* # Clean up apt cache to keep image smaller

# Set the working directory inside the container
WORKDIR /app

# Upgrade pip (good practice)
RUN pip install --upgrade pip

# Copy requirements.txt first to leverage Docker layer caching
# If requirements.txt doesn't change, this layer won't rebuild
COPY requirements.txt /app/

# Install Python dependencies from requirements.txt
# --no-cache-dir reduces image size by not storing pip's cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your Django project code
COPY . /app/

# Expose the port Django will run on
EXPOSE 8000

# Command to run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]