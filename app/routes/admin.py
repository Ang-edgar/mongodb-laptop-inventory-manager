from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from bson import ObjectId
from datetime import datetime, timedelta
import base64
from models import LaptopModel, SparePartModel, OrderModel, WarrantyModel
from .auth import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    laptop_model = LaptopModel(current_app.db)
    order_model = OrderModel(current_app.db)
    
    stats = {
        'total_laptops': current_app.db.laptops.count_documents({}),
        'available_laptops': current_app.db.laptops.count_documents({'status': 'available'}),
        'sold_laptops': current_app.db.laptops.count_documents({'status': 'sold'}),
        'pending_orders': current_app.db.orders.count_documents({'status': 'unconfirmed'}),
        'total_orders': current_app.db.orders.count_documents({})
    }
    
    recent_laptops = laptop_model.find_all()[-5:]  # Last 5 laptops
    recent_orders = order_model.find_all()[:5]  # First 5 orders
    
    return render_template('admin/dashboard.html', stats=stats, 
                         recent_laptops=recent_laptops, recent_orders=recent_orders)

@bp.route('/laptops')
@admin_required
def laptops():
    """Manage laptops"""
    laptop_model = LaptopModel(current_app.db)
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        laptops = laptop_model.find_all()
    else:
        laptops = laptop_model.find_all(status=status_filter)
    
    return render_template('admin/laptops.html', laptops=laptops, status_filter=status_filter)

@bp.route('/laptops/add', methods=['GET', 'POST'])
@admin_required
def add_laptop():
    """Add new laptop"""
    if request.method == 'POST':
        # Process screen size to add quote mark for display
        screen_size = request.form.get('screen_size')
        if screen_size:
            screen_size = screen_size + '"'
        
        laptop_data = {
            'brand': request.form.get('brand'),
            'model': request.form.get('model'),
            'cpu': request.form.get('cpu'),
            'ram': request.form.get('ram'),
            'storage': request.form.get('storage'),
            'screen_size': screen_size,
            'graphics': request.form.get('graphics'),
            'os': request.form.get('os'),
            'condition': request.form.get('condition'),
            'purchase_price': float(request.form.get('purchase_price', 0)),
            'selling_price': float(request.form.get('selling_price', 0)),
            'date_purchased': datetime.strptime(request.form.get('date_purchased'), '%Y-%m-%d'),
            'description': request.form.get('description', ''),
            'status': 'available'
        }
        
        # Handle image upload
        if 'image' in request.files and request.files['image'].filename:
            image_file = request.files['image']
            # Convert image to base64
            laptop_data['image'] = base64.b64encode(image_file.read()).decode('utf-8')
            laptop_data['image_filename'] = image_file.filename
        
        laptop_model = LaptopModel(current_app.db)
        laptop_id = laptop_model.create(laptop_data)
        
        flash('Laptop added successfully!', 'success')
        return redirect(url_for('admin.laptops'))
    
    return render_template('admin/add_laptop.html')

@bp.route('/laptops/<laptop_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_laptop(laptop_id):
    """Edit laptop"""
    laptop_model = LaptopModel(current_app.db)
    laptop = laptop_model.find_by_id(laptop_id)
    
    if not laptop:
        flash('Laptop not found', 'error')
        return redirect(url_for('admin.laptops'))
    
    if request.method == 'POST':
        # Process screen size to add quote mark for display
        screen_size = request.form.get('screen_size')
        if screen_size:
            screen_size = screen_size + '"'
        
        update_data = {
            'brand': request.form.get('brand'),
            'model': request.form.get('model'),
            'cpu': request.form.get('cpu'),
            'ram': request.form.get('ram'),
            'storage': request.form.get('storage'),
            'screen_size': screen_size,
            'graphics': request.form.get('graphics'),
            'os': request.form.get('os'),
            'condition': request.form.get('condition'),
            'purchase_price': float(request.form.get('purchase_price', 0)),
            'selling_price': float(request.form.get('selling_price', 0)),
            'description': request.form.get('description', ''),
            'status': request.form.get('status')
        }
        
        # Handle date
        if request.form.get('date_purchased'):
            update_data['date_purchased'] = datetime.strptime(
                request.form.get('date_purchased'), '%Y-%m-%d'
            )
        
        # Handle image upload
        if 'image' in request.files and request.files['image'].filename:
            image_file = request.files['image']
            update_data['image'] = base64.b64encode(image_file.read()).decode('utf-8')
            update_data['image_filename'] = image_file.filename
        
        laptop_model.update(laptop_id, update_data)
        flash('Laptop updated successfully!', 'success')
        return redirect(url_for('admin.laptops'))
    
    return render_template('admin/edit_laptop.html', laptop=laptop)

@bp.route('/laptops/<laptop_id>/delete', methods=['POST'])
@admin_required
def delete_laptop(laptop_id):
    """Delete laptop"""
    laptop_model = LaptopModel(current_app.db)
    laptop_model.delete(laptop_id)
    flash('Laptop deleted successfully!', 'success')
    return redirect(url_for('admin.laptops'))

@bp.route('/spare-parts', methods=['GET', 'POST'])
@admin_required
def spare_parts():
    """Manage spare parts"""
    spare_part_model = SparePartModel(current_app.db)
    
    if request.method == 'POST':
        # Create new spare part
        name = request.form.get('name')
        part_type = request.form.get('type')
        price = float(request.form.get('price', 0))
        quantity = int(request.form.get('quantity', 0))
        description = request.form.get('description', '')
        
        part_data = {
            'name': name,
            'type': part_type,
            'price': price,
            'quantity': quantity,
            'description': description
        }
        
        spare_part_model.create(part_data)
        flash('Spare part added successfully!', 'success')
        return redirect(url_for('admin.spare_parts'))
    
    parts = spare_part_model.find_all()
    return render_template('admin/spare_parts.html', parts=parts)

@bp.route('/spare-parts/<part_id>/edit', methods=['POST'])
@admin_required
def edit_spare_part(part_id):
    """Edit spare part"""
    spare_part_model = SparePartModel(current_app.db)
    
    name = request.form.get('name')
    part_type = request.form.get('type')
    price = float(request.form.get('price', 0))
    quantity = int(request.form.get('quantity', 0))
    description = request.form.get('description', '')
    
    update_data = {
        'name': name,
        'type': part_type,
        'price': price,
        'quantity': quantity,
        'description': description
    }
    
    spare_part_model.update(part_id, update_data)
    flash('Spare part updated successfully!', 'success')
    return redirect(url_for('admin.spare_parts'))

@bp.route('/spare-parts/<part_id>/delete', methods=['POST'])
@admin_required
def delete_spare_part(part_id):
    """Delete spare part"""
    spare_part_model = SparePartModel(current_app.db)
    spare_part_model.delete(part_id)
    flash('Spare part deleted successfully!', 'success')
    return redirect(url_for('admin.spare_parts'))

@bp.route('/orders')
@admin_required
def orders():
    """Manage orders"""
    order_model = OrderModel(current_app.db)
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        orders = order_model.find_all()
    else:
        orders = order_model.find_all(status=status_filter)
    
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@bp.route('/orders/<order_id>/update-status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Update order status"""
    new_status = request.form.get('status')
    order_model = OrderModel(current_app.db)
    order_model.update_status(order_id, new_status)
    
    # If marking as completed, update laptop status to sold
    if new_status == 'completed':
        order = order_model.find_by_id(order_id)
        if order and 'items' in order:
            laptop_model = LaptopModel(current_app.db)
            for item in order['items']:
                laptop_model.update(item['laptop_id'], {'status': 'sold', 'date_sold': datetime.utcnow()})
    
    flash('Order status updated successfully!', 'success')
    return redirect(url_for('admin.orders'))

@bp.route('/warranties')
@admin_required
def warranties():
    """Manage warranties"""
    warranty_model = WarrantyModel(current_app.db)
    warranties = warranty_model.find_all()
    
    # Add laptop details to warranties
    laptop_model = LaptopModel(current_app.db)
    for warranty in warranties:
        laptop = laptop_model.find_by_id(warranty['laptop_id'])
        warranty['laptop'] = laptop
        
        # Calculate days remaining
        if warranty['end_date'] > datetime.utcnow():
            warranty['days_remaining'] = (warranty['end_date'] - datetime.utcnow()).days
        else:
            warranty['days_remaining'] = 0
    
    return render_template('admin/warranties.html', warranties=warranties)