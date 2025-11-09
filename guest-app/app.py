from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify, make_response
import requests
import os
from dotenv import load_dotenv
from auth import register_user, login_user, get_current_user

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'guest-secret-key-2025')

# Admin API URL
ADMIN_API_URL = os.environ.get('ADMIN_API_URL', 'http://localhost:5000/api')

# Context processor to make user available in all templates
@app.context_processor
def inject_user():
    return dict(user=get_current_user())

# Helper function to call admin API
def call_api(endpoint, method='GET', data=None):
    """Call admin API"""
    url = f"{ADMIN_API_URL}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, params=data, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return {'success': False, 'error': str(e)}

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        # Register user
        result = register_user(email, password, name)
        
        if result['success']:
            # Set token in cookie
            response = make_response(redirect(url_for('shop')))
            response.set_cookie('auth_token', result['token'], 
                              max_age=86400, httponly=True, samesite='Lax')
            flash(f"Welcome {name}! Your account has been created.", 'success')
            return response
        else:
            flash(result['error'], 'error')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Login user
        result = login_user(email, password)
        
        if result['success']:
            # Set token in cookie
            response = make_response(redirect(url_for('shop')))
            response.set_cookie('auth_token', result['token'], 
                              max_age=86400, httponly=True, samesite='Lax')
            flash(f"Welcome back, {result['user']['name']}!", 'success')
            return response
        else:
            flash(result['error'], 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    response = make_response(redirect(url_for('index')))
    response.set_cookie('auth_token', '', expires=0)
    flash('You have been logged out', 'info')
    return response


@app.route('/')
def index():
    """Homepage"""
    # Get current user
    user = get_current_user()
    
    # Get featured laptops from API
    result = call_api('/laptops')
    laptops = result.get('laptops', [])[:6] if result.get('success') else []
    return render_template('index.html', laptops=laptops, user=user)

@app.route('/shop')
def shop():
    """Shop page - browse all laptops"""
    result = call_api('/laptops')
    laptops = result.get('laptops', []) if result.get('success') else []
    return render_template('shop.html', laptops=laptops)

@app.route('/laptop/<laptop_id>')
def laptop_detail(laptop_id):
    """Laptop detail page"""
    # Get laptop details
    laptop_result = call_api(f'/laptops/{laptop_id}')
    if not laptop_result.get('success'):
        flash('Laptop not found', 'error')
        return redirect(url_for('shop'))
    
    # Get spare parts
    parts_result = call_api('/spare-parts')
    spare_parts = parts_result.get('spare_parts', []) if parts_result.get('success') else []
    
    return render_template('laptop_detail.html', 
                         laptop=laptop_result['laptop'], 
                         spare_parts=spare_parts)

@app.route('/cart')
def cart():
    """Shopping cart"""
    cart_items = session.get('cart', [])
    
    # Fetch current prices from API
    for item in cart_items:
        laptop_result = call_api(f"/laptops/{item['laptop_id']}")
        if laptop_result.get('success'):
            item['laptop'] = laptop_result['laptop']
        
        # Fetch spare parts details
        for part in item.get('spare_parts', []):
            part_result = call_api(f"/spare-parts/{part['part_id']}")
            if part_result.get('success'):
                part.update(part_result['spare_part'])
    
    # Calculate total price
    total_price = sum(item['total_price'] for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    data = request.get_json()
    
    if 'cart' not in session:
        session['cart'] = []
    
    cart_item = {
        'laptop_id': data['laptop_id'],
        'laptop_brand': data['laptop_brand'],
        'laptop_model': data['laptop_model'],
        'base_price': data['base_price'],
        'spare_parts': data.get('spare_parts', []),
        'total_price': data['total_price']
    }
    
    session['cart'].append(cart_item)
    session.modified = True
    
    return jsonify({'success': True, 'cart_count': len(session['cart'])})

@app.route('/cart/remove/<int:index>', methods=['POST'])
def remove_from_cart(index):
    """Remove item from cart"""
    if 'cart' in session and 0 <= index < len(session['cart']):
        session['cart'].pop(index)
        session.modified = True
        flash('Item removed from cart', 'success')
    return redirect(url_for('cart'))

@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    """Clear cart"""
    session['cart'] = []
    session.modified = True
    flash('Cart cleared', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout page"""
    cart_items = session.get('cart', [])
    
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('shop'))
    
    if request.method == 'POST':
        # Prepare order data
        order_data = {
            'customer_name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'address': request.form['address'],
            'items': cart_items
        }
        
        # Submit order to admin API
        result = call_api('/orders', method='POST', data=order_data)
        
        if result.get('success'):
            order_id = result['order_id']
            session['cart'] = []
            session.modified = True
            flash(f'Order placed successfully! Order ID: {order_id}', 'success')
            return redirect(url_for('order_confirmation', order_id=order_id))
        else:
            flash(f"Order failed: {result.get('error', 'Unknown error')}", 'error')
    
    # Calculate cart total
    cart_total = sum(item['total_price'] for item in cart_items)
    
    return render_template('checkout.html', cart_items=cart_items, cart_total=cart_total)

@app.route('/order/<order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    result = call_api(f'/orders/{order_id}')
    
    if not result.get('success'):
        flash('Order not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('order_confirmation.html', order=result['order'])

@app.route('/track-order', methods=['GET', 'POST'])
def track_order():
    """Track order page"""
    if request.method == 'POST':
        email = request.form['email']
        order_id = request.form['order_id']
        
        result = call_api('/orders/lookup', data={'email': email, 'order_id': order_id})
        
        if result.get('success'):
            return render_template('track_order.html', order=result['order'])
        else:
            flash('Order not found. Please check your email and order ID.', 'error')
    
    return render_template('track_order.html', order=None)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
