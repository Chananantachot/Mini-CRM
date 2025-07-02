# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy your application code
COPY . .

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y build-essential libssl-dev \
    && pip install --no-cache-dir -r requirements.txt

# Make sure gevent is installed
# Flask-SocketIO requires specific versions sometimes, so be precise if needed
RUN pip install gevent gevent-websocket

# Expose port 443 for HTTPS if you run build dockerFile  
EXPOSE 5000

# Run the app
CMD ["python3", "app.py"]
