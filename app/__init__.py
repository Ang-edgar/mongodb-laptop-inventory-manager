from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'laptop-inventory-secret-key-2025')
    
    # Enable CORS for API endpoints
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",  # In production, specify allowed origins
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # MongoDB connection
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/laptop_inventory')
    client = MongoClient(mongodb_uri)
    
    # Make database available to app
    app.db = client.get_default_database()
    
    # Initialize collections with indexes
    init_database(app.db)
    
    # Register blueprints
    from routes import main, auth, admin, guest, api
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(guest.bp)
    app.register_blueprint(api.api)  # Register API blueprint
    
    return app

def init_database(db):
    """Initialize MongoDB collections and indexes"""
    # Create indexes for better performance
    db.laptops.create_index("serial_number", unique=True)
    db.laptops.create_index("status")
    db.laptops.create_index("brand")
    
    db.spare_parts.create_index("name")
    db.spare_parts.create_index("type")
    
    db.orders.create_index("order_id", unique=True)
    db.orders.create_index("email")
    db.orders.create_index("status")
    
    db.warranties.create_index("laptop_id")
    db.warranties.create_index("end_date")
    
    # Create default admin user if not exists
    if not db.users.find_one({"username": "admin"}):
        from werkzeug.security import generate_password_hash
        db.users.insert_one({
            "username": "admin",
            "password": generate_password_hash("admin123"),
            "role": "admin"
        })

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)