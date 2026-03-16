import pytest
from app import User

def test_index_page(client):
    """Test that index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Coligame" in response.data

def test_login_page(client):
    """Test that login page loads correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_registration(client, app, db):
    """Test user registration."""
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'test@example.com'

def test_invalid_login(client):
    """Test login with invalid credentials."""
    response = client.post('/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b"Invalid username or password" in response.data
