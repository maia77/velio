#!/usr/bin/env python3
"""
Main application entry point for deployment platforms.
This file serves as the entry point that deployment platforms expect.
"""

import os
import sys
from pathlib import Path

# Add the web directory to Python path
web_dir = Path(__file__).parent / "web"
sys.path.insert(0, str(web_dir))

# Change to web directory
os.chdir(web_dir)

# Import the Flask app from web directory
from app import app

if __name__ == "__main__":
    # Get port from environment variable (for deployment platforms)
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)
