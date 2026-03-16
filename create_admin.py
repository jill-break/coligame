from app import app, db, User
from werkzeug.security import generate_password_hash
import sys

def create_admin(username, email, password):
    with app.app_context():
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User {username} already exists. Promoting to admin...")
            user.is_admin = True
        else:
            print(f"Creating new admin user {username}...")
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                is_admin=True
            )
            db.session.add(user)
        
        db.session.commit()
        print("Success! Admin created/promoted.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <username> <email> <password>")
    else:
        create_admin(sys.argv[1], sys.argv[2], sys.argv[3])
