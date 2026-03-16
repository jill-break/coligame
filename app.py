from src.app import app, socketio, db

# Create tables if they don't exist (Runs on import for Gunicorn)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    socketio.run(app, debug=True)
