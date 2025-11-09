"""
User authentication module with JWT tokens
Kubernetes-ready: stateless authentication
"""
import jwt
import bcrypt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from pymongo import MongoClient

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# MongoDB connection
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://mongodb:27017/')
client = MongoClient(MONGODB_URI)
db = client['laptop_inventory']
users_collection = db['users']

# Create indexes
users_collection.create_index('email', unique=True)


def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)


def generate_token(user_id, email):
    """Generate JWT token"""
    payload = {
        'user_id': str(user_id),
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def register_user(email, password, name):
    """Register a new user"""
    # Check if user exists
    if users_collection.find_one({'email': email}):
        return {'success': False, 'error': 'Email already registered'}
    
    # Create user
    user = {
        'email': email,
        'password': hash_password(password),
        'name': name,
        'created_at': datetime.utcnow(),
        'is_active': True
    }
    
    result = users_collection.insert_one(user)
    
    # Generate token
    token = generate_token(result.inserted_id, email)
    
    return {
        'success': True,
        'token': token,
        'user': {
            'id': str(result.inserted_id),
            'email': email,
            'name': name
        }
    }


def login_user(email, password):
    """Login user and return JWT token"""
    user = users_collection.find_one({'email': email})
    
    if not user:
        return {'success': False, 'error': 'Invalid email or password'}
    
    if not verify_password(password, user['password']):
        return {'success': False, 'error': 'Invalid email or password'}
    
    if not user.get('is_active', True):
        return {'success': False, 'error': 'Account is deactivated'}
    
    # Generate token
    token = generate_token(user['_id'], user['email'])
    
    return {
        'success': True,
        'token': token,
        'user': {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user['name']
        }
    }


def get_user_from_token(token):
    """Get user data from token"""
    payload = decode_token(token)
    if not payload:
        return None
    
    user = users_collection.find_one({'email': payload['email']})
    if not user:
        return None
    
    return {
        'id': str(user['_id']),
        'email': user['email'],
        'name': user['name']
    }


def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1]
        user = get_user_from_token(token)
        
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user to request context
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """Get current authenticated user from cookie or header"""
    # Try cookie first (for web interface)
    token = request.cookies.get('auth_token')
    
    # Try Authorization header (for API)
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    if not token:
        return None
    
    return get_user_from_token(token)
