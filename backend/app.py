"""
DevFlow Backend – Flask API Server
===================================
Entry point for the DevFlow AI Developer Productivity Dashboard API.
Run: python app.py
"""

from flask import Flask
from flask_cors import CORS
from routes import register_routes

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes so the frontend can fetch from a different origin

# Register all API routes from routes.py
register_routes(app)

if __name__ == "__main__":
    print("🚀 DevFlow API server starting on http://localhost:5000")
    app.run(debug=True, port=5000)
