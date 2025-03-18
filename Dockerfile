# Use official Python image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run ASGI server (Daphne for WebSockets)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "studypal.asgi:application"]
