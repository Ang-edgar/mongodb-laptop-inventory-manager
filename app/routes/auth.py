from flask import Blueprint, request, render_template, redirect, url_for, session, flash, current_app
from werkzeug.security import check_password_hash
from models import UserModel

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_model = UserModel(current_app.db)
        user = user_model.find_by_username(username)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))

def login_required(f):
    """Decorator to require login"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function