from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, jsonify
from bson import ObjectId
from datetime import datetime
from models import LaptopModel, OrderModel, SparePartModel

bp = Blueprint('guest', __name__, url_prefix='/shop')

@bp.route('/')
def shop():
    """Guest shop - browse available laptops"""
    laptop_model = LaptopModel(current_app.db)
    
    # Get filter parameters
    brand_filter = request.args.get('brand', '')
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)
    
    # Build query
    query = {'status': 'available'}
    if brand_filter:
        query['brand'] = {'$regex': brand_filter, '$options': 'i'}
    if price_min is not None or price_max is not None:
        query['selling_price'] = {}
        if price_min is not None:
            query['selling_price']['$gte'] = price_min
        if price_max is not None:
            query['selling_price']['$lte'] = price_max
    
    laptops = list(current_app.db.laptops.find(query))
    
    # Get unique brands for filter
    brands = current_app.db.laptops.distinct('brand', {'status': 'available'})
    
    return render_template('guest/shop.html', laptops=laptops, brands=brands,
                         brand_filter=brand_filter, price_min=price_min, price_max=price_max)

@bp.route('/laptop/<laptop_id>')
def laptop_detail(laptop_id):
    """Laptop detail page"""
    laptop_model = LaptopModel(current_app.db)
    laptop = laptop_model.find_by_id(laptop_id)
    
    if not laptop or laptop['status'] != 'available':
        flash('Laptop not found or not available', 'error')
        return redirect(url_for('guest.shop'))
    
    # Get available spare parts for customization
    spare_part_model = SparePartModel(current_app.db)
    ram_parts = spare_part_model.find_all('RAM')
    storage_parts = spare_part_model.find_all('Storage')
    
    return render_template('guest/laptop_detail.html', laptop=laptop,
                         ram_parts=ram_parts, storage_parts=storage_parts)

@bp.route('/cart')
def cart():
    """View cart"""
    cart_items = session.get('cart', [])
    
    # Get laptop details for cart items
    laptop_model = LaptopModel(current_app.db)
    spare_part_model = SparePartModel(current_app.db)
    
    detailed_cart = []
    total_price = 0
    
    for item in cart_items:
        laptop = laptop_model.find_by_id(item['laptop_id'])
        if laptop:
            cart_item = {
                'laptop': laptop,
                'base_price': laptop['selling_price'],
                'spare_parts': [],
                'total_price': laptop['selling_price']
            }
            
            # Add spare parts details
            for part_id in item.get('spare_parts', []):
                part = spare_part_model.find_by_id(part_id)
                if part:
                    cart_item['spare_parts'].append(part)
                    cart_item['total_price'] += part.get('price', 0)
            
            detailed_cart.append(cart_item)
            total_price += cart_item['total_price']
    
    return render_template('guest/cart.html', cart_items=detailed_cart, total_price=total_price)

@bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """Add laptop to cart with customizations"""
    laptop_id = request.form.get('laptop_id')
    spare_parts = request.form.getlist('spare_parts')
    
    # Initialize cart if not exists
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if laptop already in cart
    cart = session['cart']
    existing_item = None
    for item in cart:
        if item['laptop_id'] == laptop_id:
            existing_item = item
            break
    
    if existing_item:
        # Update existing item
        existing_item['spare_parts'] = spare_parts
    else:
        # Add new item
        cart.append({
            'laptop_id': laptop_id,
            'spare_parts': spare_parts
        })
    
    session['cart'] = cart
    session.modified = True
    
    flash('Laptop added to cart!', 'success')
    return redirect(url_for('guest.cart'))

@bp.route('/cart/add', methods=['POST'])
def add_to_cart_ajax():
    """Add laptop to cart via AJAX"""
    try:
        data = request.get_json()
        laptop_id = data.get('laptop_id')
        quantity = data.get('quantity', 1)
        
        if not laptop_id:
            return jsonify({'success': False, 'message': 'Laptop ID is required'})
        
        # Verify laptop exists and is available
        laptop_model = LaptopModel(current_app.db)
        laptop = laptop_model.find_by_id(laptop_id)
        
        if not laptop:
            return jsonify({'success': False, 'message': 'Laptop not found'})
            
        if laptop.get('status') != 'available':
            return jsonify({'success': False, 'message': 'Laptop is not available'})
        
        # Initialize cart if not exists
        if 'cart' not in session:
            session['cart'] = []
        
        # Check if laptop already in cart
        cart = session['cart']
        existing_item = None
        for item in cart:
            if item['laptop_id'] == laptop_id:
                existing_item = item
                break
        
        if existing_item:
            # Update quantity if item already exists
            existing_item['quantity'] = existing_item.get('quantity', 1) + quantity
        else:
            # Add new item
            cart.append({
                'laptop_id': laptop_id,
                'quantity': quantity,
                'spare_parts': []
            })
        
        session['cart'] = cart
        session.modified = True
        
        return jsonify({
            'success': True, 
            'message': 'Laptop added to cart successfully',
            'cart_count': len(cart)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/remove-from-cart/<laptop_id>')
def remove_from_cart(laptop_id):
    """Remove laptop from cart"""
    if 'cart' in session:
        cart = session['cart']
        session['cart'] = [item for item in cart if item['laptop_id'] != laptop_id]
        session.modified = True
        flash('Item removed from cart', 'info')
    
    return redirect(url_for('guest.cart'))

@bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout process"""
    cart_items = session.get('cart', [])
    
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('guest.shop'))
    
    if request.method == 'POST':
        # Create order
        order_data = {
            'customer_name': request.form.get('customer_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'items': [],
            'total_amount': 0
        }
        
        # Process cart items
        laptop_model = LaptopModel(current_app.db)
        spare_part_model = SparePartModel(current_app.db)
        
        for cart_item in cart_items:
            laptop = laptop_model.find_by_id(cart_item['laptop_id'])
            if laptop and laptop['status'] == 'available':
                item_total = laptop['selling_price']
                spare_parts_details = []
                
                for part_id in cart_item.get('spare_parts', []):
                    part = spare_part_model.find_by_id(part_id)
                    if part:
                        spare_parts_details.append({
                            'part_id': part_id,
                            'name': part['name'],
                            'price': part.get('price', 0)
                        })
                        item_total += part.get('price', 0)
                
                order_data['items'].append({
                    'laptop_id': cart_item['laptop_id'],
                    'laptop_brand': laptop['brand'],
                    'laptop_model': laptop['model'],
                    'base_price': laptop['selling_price'],
                    'spare_parts': spare_parts_details,
                    'total_price': item_total
                })
                
                order_data['total_amount'] += item_total
        
        # Create order
        order_model = OrderModel(current_app.db)
        order_id = order_model.create(order_data)
        
        # Clear cart
        session.pop('cart', None)
        
        flash('Order placed successfully! You will receive a confirmation email.', 'success')
        return redirect(url_for('guest.order_confirmation', order_id=order_data['order_id']))
    
    # Calculate cart total for display
    laptop_model = LaptopModel(current_app.db)
    spare_part_model = SparePartModel(current_app.db)
    
    cart_total = 0
    detailed_cart = []
    
    for item in cart_items:
        laptop = laptop_model.find_by_id(item['laptop_id'])
        if laptop:
            quantity = item.get('quantity', 1)
            item_total = laptop['selling_price'] * quantity
            spare_parts = []
            
            for part_id in item.get('spare_parts', []):
                part = spare_part_model.find_by_id(part_id)
                if part:
                    spare_parts.append(part)
                    item_total += part.get('price', 0)
            
            detailed_cart.append({
                'laptop': laptop,
                'spare_parts': spare_parts,
                'quantity': quantity,
                'total_price': item_total
            })
            cart_total += item_total
    
    return render_template('guest/checkout.html', cart_items=detailed_cart, cart_total=cart_total)

@bp.route('/order-confirmation/<order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    order_model = OrderModel(current_app.db)
    order = order_model.find_by_order_id(order_id)
    
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('guest.shop'))
    
    return render_template('guest/order_confirmation.html', order=order)

@bp.route('/order-lookup', methods=['GET', 'POST'])
def order_lookup():
    """Look up order by email and order ID"""
    order = None
    
    if request.method == 'POST':
        email = request.form.get('email')
        order_id = request.form.get('order_id')
        
        order_model = OrderModel(current_app.db)
        order = current_app.db.orders.find_one({
            'email': email,
            'order_id': order_id
        })
        
        if not order:
            flash('Order not found. Please check your email and order ID.', 'error')
    
    return render_template('guest/order_lookup.html', order=order)