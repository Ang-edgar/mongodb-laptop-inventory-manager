from flask import Blueprint, jsonify, request, current_app
from bson import ObjectId
from datetime import datetime
from app.models.database import LaptopModel, SparePartModel, OrderModel

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

# GET /api/laptops - List all available laptops
@api.route('/laptops', methods=['GET'])
def get_laptops():
    """Get all available laptops"""
    try:
        laptop_model = LaptopModel(current_app.db)
        # Get all laptops with status 'available'
        laptops = list(current_app.db.laptops.find({'status': 'available'}))
        
        # Serialize laptops
        serialized_laptops = [serialize_doc(laptop) for laptop in laptops]
        
        return jsonify({
            'success': True,
            'laptops': serialized_laptops
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# GET /api/laptops/<id> - Get single laptop details
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

# GET /api/spare-parts - List all spare parts
@api.route('/spare-parts', methods=['GET'])
def get_spare_parts():
    """Get all spare parts"""
    try:
        spare_part_model = SparePartModel(current_app.db)
        spare_parts = spare_part_model.find_all()
        
        serialized_parts = [serialize_doc(part) for part in spare_parts]
        
        return jsonify({
            'success': True,
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
        'service': 'laptop-inventory-admin-api'
    }), 200
