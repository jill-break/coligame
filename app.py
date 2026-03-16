from src.app import app, socketio, db

# This root-level app.py is the entry point for production (Gunicorn)
# It imports the app instance from the src directory

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
