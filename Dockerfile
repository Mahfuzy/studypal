# Use official Python image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies (for Pillow, psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip before installing dependencies
RUN python -m pip install --upgrade pip

# Copy dependency list first (to leverage Docker caching)
COPY requirements.txt .

# Install Python dependencies with increased timeout
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run ASGI server (Daphne for WebSockets)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "studypal.asgi:application"]
