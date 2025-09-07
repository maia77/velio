#!/bin/bash

# Deployment script for various platforms
echo "🚀 Starting deployment process..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the project root."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p web/static/uploads
mkdir -p web/instance/flask_session

# Set permissions
echo "🔐 Setting permissions..."
chmod +x app.py
chmod +x wsgi.py

echo "✅ Deployment preparation complete!"
echo ""
echo "For different platforms:"
echo "• Render.com: Use render.yaml configuration"
echo "• Heroku: Use Procfile"
echo "• Docker: Use Dockerfile"
echo "• Direct: Run 'python app.py'"
