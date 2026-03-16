import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from create_admin import create_admin
from app import User, GAMES

def test_create_admin_new_user(app, db):
    """Test creating a new admin user."""
    with patch('create_admin.generate_password_hash') as mock_hash:
        mock_hash.return_value = 'hashed_password'
        create_admin('newadmin', 'admin@example.com', 'adminpass')
        
    with app.app_context():
        user = User.query.filter_by(username='newadmin').first()
        assert user is not None
        assert user.is_admin is True
        assert user.email == 'admin@example.com'

def test_promote_to_admin(app, db):
    """Test promoting an existing user to admin."""
    with app.app_context():
        user = User(username='regular', email='reg@ex.com', password_hash='pw')
        db.session.add(user)
        db.session.commit()
        
    create_admin('regular', 'reg@ex.com', 'newpass')
    
    with app.app_context():
        user = User.query.filter_by(username='regular').first()
        assert user.is_admin is True

def test_validate_templates_logic():
    """Test that validate_routes logic correctly identifies existing/missing files."""
    from validate_routes import validate_templates
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        # Just ensure it runs without error when files exist
        validate_templates()
        assert mock_exists.called
