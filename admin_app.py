#!/usr/bin/env python3
"""
Admin application entry point for deployment platforms.
This file serves as the entry point for the admin application.
"""

import os
import sys
from pathlib import Path

# Add the admin-app directory to Python path
admin_dir = Path(__file__).parent / "admin-app"
sys.path.insert(0, str(admin_dir))

# Change to admin-app directory
os.chdir(admin_dir)

# Import the Flask app from admin-app directory
from admin_app_fixed import app

if __name__ == "__main__":
    # Get port from environment variable (for deployment platforms)
    port = int(os.environ.get('PORT', 5007))
    app.run(host='0.0.0.0', port=port, debug=False)
