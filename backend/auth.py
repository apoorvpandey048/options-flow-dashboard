"""
Authentication module - JWT-based auth
"""
import jwt
import os
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# Enforce strong JWT secret - fail if not set in production
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
if SECRET_KEY == 'dev-secret-key-change-in-production' and os.getenv('FLASK_ENV') == 'production':
    raise ValueError("JWT_SECRET_KEY must be set to a strong secret in production!")

# Use absolute path for users.json to avoid creating multiple databases
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.json')

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def generate_token(username):
    """Generate JWT token"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to protect routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        username = verify_token(token)
        if not username:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(username, *args, **kwargs)
    
    return decorated

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, None

def register_user(username, password, email):
    """Register new user"""
    users = load_users()
    
    if username in users:
        return None, 'Username already exists'
    
    # Validate email
    if email and not validate_email(email):
        return None, 'Invalid email format'
    
    # Validate password strength
    is_valid, error = validate_password(password)
    if not is_valid:
        return None, error
    
    users[username] = {
        'password': generate_password_hash(password),
        'email': email,
        'created_at': datetime.now().isoformat()
    }
    
    save_users(users)
    token = generate_token(username)
    return token, None

def login_user(username, password):
    """Login user"""
    users = load_users()
    
    if username not in users:
        return None, 'Invalid credentials'
    
    if not check_password_hash(users[username]['password'], password):
        return None, 'Invalid credentials'
    
    token = generate_token(username)
    return token, None
