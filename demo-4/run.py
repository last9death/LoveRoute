#!/usr/bin/env python3
"""
LoveRoute Development Server
Quick script to run the Flask application
"""

import os
import sys
from app import app, init_db

if __name__ == '__main__':
    # Initialize database
    print("Initializing database...")
    init_db()
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    print("Starting LoveRoute development server...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)