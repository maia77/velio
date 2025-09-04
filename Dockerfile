# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p web/static/uploads
RUN mkdir -p admin-app/static/uploads
RUN mkdir -p web/instance/flask_session

# Set environment variables
ENV FLASK_APP=web/app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 5003 5007

# Create startup script
RUN echo '#!/bin/bash\n\
cd web && python app.py &\n\
cd ../admin-app && python admin_app_fixed.py &\n\
wait' > /app/start.sh && chmod +x /app/start.sh

# Default command
CMD ["/app/start.sh"]
