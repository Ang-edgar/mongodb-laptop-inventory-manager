from flask import Blueprint, jsonify, request, current_app
from bson import ObjectId
from datetime import datetime
from app.models.database import LaptopModel, SparePartModel, OrderModel
from functools import wraps

api = Blueprint('api', __name__, url_prefix='/api')

# Helper function to serialize MongoDB documents
def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None
    doc['_id'] = str(doc['_id'])
    if 'laptop_id' in doc and isinstance(doc['laptop_id'], ObjectId):
        doc['laptop_id'] = str(doc['laptop_id'])
    return doc

# API Key authentication decorator (optional - for admin operations)
def require_api_key(f):
    """Decorator to require API key for admin operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        # For now, check if admin session exists OR valid API key
        # In production, use proper API key validation
        if not api_key and not request.cookies.get('admin_logged_in'):
            return jsonify({
                'success': False,
                'error': 'Unauthorized - API key required'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# LAPTOPS ENDPOINTS - Full CRUD
# ============================================================================

# GET /api/laptops - List all laptops (with optional filters)
@api.route('/laptops', methods=['GET'])
def get_laptops():
    """Get all laptops with optional filtering"""
    try:
        # Query parameters for filtering
        status = request.args.get('status', 'available')
        brand = request.args.get('brand')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        
        # Build query
        query = {}
        if status:
            query['status'] = status
        if brand:
            query['brand'] = {'$regex': brand, '$options': 'i'}
        if min_price or max_price:
            query['selling_price'] = {}
            if min_price:
                query['selling_price']['$gte'] = float(min_price)
            if max_price:
                query['selling_price']['$lte'] = float(max_price)
        
        laptops = list(current_app.db.laptops.find(query))
        serialized_laptops = [serialize_doc(laptop) for laptop in laptops]
        
        return jsonify({
            'success': True,
            'count': len(serialized_laptops),
            'laptops': serialized_laptops
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# GET /api/laptops/<id> - Get single laptop
@api.route('/laptops/<laptop_id>', methods=['GET'])
def get_laptop(laptop_id):
    """Get laptop by ID"""
    try:
        laptop_model = LaptopModel(current_app.db)
        laptop = laptop_model.find_by_id(laptop_id)
        
        if not laptop:
            return jsonify({
                'success': False,
                'error': 'Laptop not found'
            }), 404
        
        return jsonify({
            'success': True,
            'laptop': serialize_doc(laptop)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# POST /api/laptops - Create new laptop (Admin only)
@api.route('/laptops', methods=['POST'])
@require_api_key
def create_laptop():
    """Create a new laptop (requires admin authentication)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['brand', 'model', 'cpu', 'ram', 'storage', 'selling_price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        laptop_model = LaptopModel(current_app.db)
        laptop_id = laptop_model.create(data)
        
        return jsonify({
            'success': True,
            'laptop_id': str(laptop_id),
            'message': 'Laptop created successfully'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# PUT /api/laptops/<id> - Full update of laptop (Admin only)
@api.route('/laptops/<laptop_id>', methods=['PUT'])
@require_api_key
def update_laptop(laptop_id):
    """Fully update a laptop (requires admin authentication)"""
    try:
        data = request.get_json()
        laptop_model = LaptopModel(current_app.db)
        
        # Check if laptop exists
        if not laptop_model.find_by_id(laptop_id):
            return jsonify({
                'success': False,
                'error': 'Laptop not found'
            }), 404
        
        # Add updated_at timestamp
        data['updated_at'] = datetime.utcnow()
        
        # Update laptop
        laptop_model.update(laptop_id, data)
        
        return jsonify({
            'success': True,
            'message': 'Laptop updated successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# PATCH /api/laptops/<id> - Partial update of laptop (Admin only)
@api.route('/laptops/<laptop_id>', methods=['PATCH'])
@require_api_key
def patch_laptop(laptop_id):
    """Partially update a laptop (requires admin authentication)"""
    try:
        data = request.get_json()
        laptop_model = LaptopModel(current_app.db)
        
        # Check if laptop exists
        if not laptop_model.find_by_id(laptop_id):
            return jsonify({
                'success': False,
                'error': 'Laptop not found'
            }), 404
        
        # Only update provided fields
        data['updated_at'] = datetime.utcnow()
        
        result = current_app.db.laptops.update_one(
            {'_id': ObjectId(laptop_id)},
            {'$set': data}
        )
        
        if result.modified_count == 0:
            return jsonify({
                'success': False,
                'message': 'No changes made'
            }), 200
        
        return jsonify({
            'success': True,
            'message': 'Laptop updated successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# DELETE /api/laptops/<id> - Delete laptop (Admin only)
@api.route('/laptops/<laptop_id>', methods=['DELETE'])
@require_api_key
def delete_laptop(laptop_id):
    """Delete a laptop (requires admin authentication)"""
    try:
        laptop_model = LaptopModel(current_app.db)
        
        # Check if laptop exists
        if not laptop_model.find_by_id(laptop_id):
            return jsonify({
                'success': False,
                'error': 'Laptop not found'
            }), 404
        
        # Delete laptop
        laptop_model.delete(laptop_id)
        
        return jsonify({
            'success': True,
            'message': 'Laptop deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# SPARE PARTS ENDPOINTS - Full CRUD
# ============================================================================

# ============================================================================
# SPARE PARTS ENDPOINTS - Full CRUD
# ============================================================================

# GET /api/spare-parts - List all spare parts
@api.route('/spare-parts', methods=['GET'])
def get_spare_parts():
    """Get all spare parts with optional filtering"""
    try:
        part_type = request.args.get('type')  # RAM or Storage
        
        query = {}
        if part_type:
            query['type'] = part_type
        
        spare_parts = list(current_app.db.spare_parts.find(query))
        serialized_parts = [serialize_doc(part) for part in spare_parts]
        
        return jsonify({
            'success': True,
            'count': len(serialized_parts),
            'spare_parts': serialized_parts
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# GET /api/spare-parts/<id> - Get single spare part
@api.route('/spare-parts/<part_id>', methods=['GET'])
def get_spare_part(part_id):
    """Get spare part by ID"""
    try:
        spare_part_model = SparePartModel(current_app.db)
        part = spare_part_model.find_by_id(part_id)
        
        if not part:
            return jsonify({
                'success': False,
                'error': 'Spare part not found'
            }), 404
        
        return jsonify({
            'success': True,
            'spare_part': serialize_doc(part)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# POST /api/spare-parts - Create new spare part (Admin only)
@api.route('/spare-parts', methods=['POST'])
@require_api_key
def create_spare_part():
    """Create a new spare part (requires admin authentication)"""
    try:
        data = request.get_json()
        
        required_fields = ['type', 'brand', 'capacity', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        spare_part_model = SparePartModel(current_app.db)
        part_id = spare_part_model.create(data)
        
        return jsonify({
            'success': True,
            'part_id': str(part_id),
            'message': 'Spare part created successfully'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# PUT /api/spare-parts/<id> - Update spare part (Admin only)
@api.route('/spare-parts/<part_id>', methods=['PUT'])
@require_api_key
def update_spare_part(part_id):
    """Update a spare part (requires admin authentication)"""
    try:
        data = request.get_json()
        spare_part_model = SparePartModel(current_app.db)
        
        if not spare_part_model.find_by_id(part_id):
            return jsonify({
                'success': False,
                'error': 'Spare part not found'
            }), 404
        
        spare_part_model.update(part_id, data)
        
        return jsonify({
            'success': True,
            'message': 'Spare part updated successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# DELETE /api/spare-parts/<id> - Delete spare part (Admin only)
@api.route('/spare-parts/<part_id>', methods=['DELETE'])
@require_api_key
def delete_spare_part(part_id):
    """Delete a spare part (requires admin authentication)"""
    try:
        spare_part_model = SparePartModel(current_app.db)
        
        if not spare_part_model.find_by_id(part_id):
            return jsonify({
                'success': False,
                'error': 'Spare part not found'
            }), 404
        
        spare_part_model.delete(part_id)
        
        return jsonify({
            'success': True,
            'message': 'Spare part deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ORDERS ENDPOINTS
# ============================================================================

# ============================================================================
# ORDERS ENDPOINTS
# ============================================================================

# POST /api/orders - Create new order
@api.route('/orders', methods=['POST'])
def create_order():
    """Create a new order from guest"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer_name', 'email', 'phone', 'address', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Prepare order data
        order_data = {
            'customer_name': data['customer_name'],
            'customer_email': data['email'],
            'customer_phone': data['phone'],
            'delivery_address': data['address'],
            'items': data['items'],
            'total_amount': sum(item.get('total_price', 0) for item in data['items']),
            'order_date': datetime.utcnow()
        }
        
        # Create order
        order_model = OrderModel(current_app.db)
        order_model.create(order_data)
        
        # Get the created order to return the order_id
        order = current_app.db.orders.find_one(
            {'customer_email': data['email']},
            sort=[('created_at', -1)]
        )
        
        return jsonify({
            'success': True,
            'order_id': order['order_id'] if order else 'Unknown',
            'message': 'Order created successfully'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# GET /api/orders/<order_id> - Get order by order ID
@api.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order by order ID"""
    try:
        order_model = OrderModel(current_app.db)
        order = order_model.find_by_order_id(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        return jsonify({
            'success': True,
            'order': serialize_doc(order)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# PATCH /api/orders/<order_id> - Update order status (Admin only)
@api.route('/orders/<order_id>', methods=['PATCH'])
@require_api_key
def update_order_status(order_id):
    """Update order status (requires admin authentication)"""
    try:
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Status field is required'
            }), 400
        
        valid_statuses = ['unconfirmed', 'confirmed', 'in progress', 'completed', 'cancelled']
        if data['status'] not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        result = current_app.db.orders.update_one(
            {'order_id': order_id},
            {'$set': {'status': data['status'], 'updated_at': datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Order status updated successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# GET /api/orders/lookup - Lookup order by email and order ID
@api.route('/orders/lookup', methods=['GET'])
def lookup_order():
    """Lookup order by email and order ID"""
    try:
        email = request.args.get('email')
        order_id = request.args.get('order_id')
        
        if not email or not order_id:
            return jsonify({
                'success': False,
                'error': 'Email and order_id are required'
            }), 400
        
        # Find order by both email and order_id
        order = current_app.db.orders.find_one({
            'customer_email': email,
            'order_id': order_id
        })
        
        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        return jsonify({
            'success': True,
            'order': serialize_doc(order)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# GET /api/health - Health check endpoint
@api.route('/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'laptop-inventory-admin-api',
        'version': '2.0.0'
    }), 200
