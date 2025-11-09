from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import os

# Database connection
def get_db():
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/laptop_inventory')
    client = MongoClient(mongodb_uri)
    return client.get_default_database()

def generate_serial_number(brand, date_purchased=None):
    """Generate a serial number based on brand and date"""
    if date_purchased is None:
        date_purchased = datetime.now()
    
    # Brand prefix mapping
    brand_prefixes = {
        'dell': 'DE', 'lenovo': 'LE', 'hp': 'HP', 'asus': 'AS',
        'acer': 'AC', 'apple': 'AP', 'toshiba': 'TO', 'samsung': 'SA',
        'msi': 'MS', 'alienware': 'AW', 'surface': 'SF'
    }
    
    brand_lower = brand.lower()
    prefix = 'UN'  # Unknown
    
    for key, value in brand_prefixes.items():
        if key in brand_lower:
            prefix = value
            break
    
    # Format: YYYYMMDD + sequential number
    date_str = date_purchased.strftime('%y%m%d')
    
    # Get count for this date to create sequential number
    db = get_db()
    count = db.laptops.count_documents({
        'date_purchased': {
            '$gte': datetime.combine(date_purchased.date(), datetime.min.time()),
            '$lt': datetime.combine(date_purchased.date(), datetime.max.time())
        }
    })
    
    return f"{prefix}{date_str}{count + 1:02d}"

class LaptopModel:
    def __init__(self, db):
        self.collection = db.laptops
    
    def create(self, laptop_data):
        """Create a new laptop"""
        laptop_data['created_at'] = datetime.utcnow()
        laptop_data['updated_at'] = datetime.utcnow()
        
        # Generate serial number if not provided
        if 'serial_number' not in laptop_data:
            laptop_data['serial_number'] = generate_serial_number(
                laptop_data.get('brand', 'Unknown'),
                laptop_data.get('date_purchased', datetime.now())
            )
        
        result = self.collection.insert_one(laptop_data)
        return result.inserted_id
    
    def find_all(self, status=None):
        """Find all laptops, optionally filtered by status"""
        query = {}
        if status:
            query['status'] = status
        return list(self.collection.find(query))
    
    def find_by_id(self, laptop_id):
        """Find laptop by ID"""
        return self.collection.find_one({'_id': ObjectId(laptop_id)})
    
    def update(self, laptop_id, update_data):
        """Update laptop"""
        update_data['updated_at'] = datetime.utcnow()
        return self.collection.update_one(
            {'_id': ObjectId(laptop_id)},
            {'$set': update_data}
        )
    
    def delete(self, laptop_id):
        """Delete laptop"""
        return self.collection.delete_one({'_id': ObjectId(laptop_id)})

class SparePartModel:
    def __init__(self, db):
        self.collection = db.spare_parts
    
    def create(self, part_data):
        """Create a new spare part"""
        part_data['created_at'] = datetime.utcnow()
        result = self.collection.insert_one(part_data)
        return result.inserted_id
    
    def find_all(self, part_type=None):
        """Find all spare parts, optionally filtered by type"""
        query = {}
        if part_type:
            query['type'] = part_type
        return list(self.collection.find(query))
    
    def find_by_id(self, part_id):
        """Find spare part by ID"""
        return self.collection.find_one({'_id': ObjectId(part_id)})
    
    def update(self, part_id, update_data):
        """Update spare part"""
        return self.collection.update_one(
            {'_id': ObjectId(part_id)},
            {'$set': update_data}
        )
    
    def delete(self, part_id):
        """Delete spare part"""
        return self.collection.delete_one({'_id': ObjectId(part_id)})

class OrderModel:
    def __init__(self, db):
        self.collection = db.orders
    
    def create(self, order_data):
        """Create a new order"""
        order_data['created_at'] = datetime.utcnow()
        order_data['status'] = 'unconfirmed'
        
        # Generate order ID
        count = self.collection.count_documents({})
        order_data['order_id'] = f"ORD{count + 1:06d}"
        
        result = self.collection.insert_one(order_data)
        return result.inserted_id
    
    def find_all(self, status=None):
        """Find all orders, optionally filtered by status"""
        query = {}
        if status:
            query['status'] = status
        return list(self.collection.find(query).sort('created_at', -1))
    
    def find_by_id(self, order_id):
        """Find order by ID"""
        return self.collection.find_one({'_id': ObjectId(order_id)})
    
    def find_by_order_id(self, order_id):
        """Find order by order_id string"""
        return self.collection.find_one({'order_id': order_id})
    
    def update_status(self, order_id, status):
        """Update order status"""
        return self.collection.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'status': status, 'updated_at': datetime.utcnow()}}
        )

class WarrantyModel:
    def __init__(self, db):
        self.collection = db.warranties
    
    def create(self, warranty_data):
        """Create a new warranty"""
        warranty_data['created_at'] = datetime.utcnow()
        result = self.collection.insert_one(warranty_data)
        return result.inserted_id
    
    def find_all(self, active_only=False):
        """Find all warranties"""
        query = {}
        if active_only:
            query['end_date'] = {'$gte': datetime.utcnow()}
        return list(self.collection.find(query))
    
    def find_by_laptop_id(self, laptop_id):
        """Find warranty by laptop ID"""
        return self.collection.find_one({'laptop_id': laptop_id})
    
    def update(self, warranty_id, update_data):
        """Update warranty"""
        return self.collection.update_one(
            {'_id': ObjectId(warranty_id)},
            {'$set': update_data}
        )
    
    def delete(self, warranty_id):
        """Delete warranty"""
        return self.collection.delete_one({'_id': ObjectId(warranty_id)})

class UserModel:
    def __init__(self, db):
        self.collection = db.users
    
    def find_by_username(self, username):
        """Find user by username"""
        return self.collection.find_one({'username': username})
    
    def create(self, user_data):
        """Create a new user"""
        user_data['created_at'] = datetime.utcnow()
        result = self.collection.insert_one(user_data)
        return result.inserted_id