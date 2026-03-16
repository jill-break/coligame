import sys
import os

# Add src to python path to allow imports from within src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from app import app, socketio, db

# Create tables if they don't exist (Runs on import for Gunicorn)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    socketio.run(app, debug=True)
