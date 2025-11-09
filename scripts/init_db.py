#!/usr/bin/env python3
"""
MongoDB Database Initialization Script
Initializes the laptop inventory database with indexes and default admin user.
"""

from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
import sys

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/laptop_inventory')

def init_database():
    """Initialize MongoDB database with collections and indexes"""
    
    print("🔄 Connecting to MongoDB...")
    try:
        client = MongoClient(MONGODB_URI)
        db_name = MONGODB_URI.split('/')[-1].split('?')[0]
        db = client[db_name]
        
        # Test connection
        client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {db_name}")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        sys.exit(1)
    
    # Create collections if they don't exist
    collections = ['laptops', 'spare_parts', 'orders', 'warranties', 'users']
    existing_collections = db.list_collection_names()
    
    for collection in collections:
        if collection not in existing_collections:
            db.create_collection(collection)
            print(f"✅ Created collection: {collection}")
        else:
            print(f"ℹ️  Collection already exists: {collection}")
    
    # Create indexes
    print("\n🔄 Creating indexes...")
    
    # Laptops indexes
    db.laptops.create_index([("serial_number", ASCENDING)], unique=True)
    db.laptops.create_index([("status", ASCENDING)])
    db.laptops.create_index([("brand", ASCENDING)])
    db.laptops.create_index([("created_at", DESCENDING)])
    db.laptops.create_index([("date_sold", DESCENDING)])
    print("✅ Created indexes for laptops collection")
    
    # Orders indexes
    db.orders.create_index([("order_id", ASCENDING)], unique=True)
    db.orders.create_index([("email", ASCENDING)])
    db.orders.create_index([("status", ASCENDING)])
    db.orders.create_index([("created_at", DESCENDING)])
    print("✅ Created indexes for orders collection")
    
    # Spare parts indexes
    db.spare_parts.create_index([("name", ASCENDING)])
    db.spare_parts.create_index([("type", ASCENDING)])
    print("✅ Created indexes for spare_parts collection")
    
    # Warranties indexes
    db.warranties.create_index([("laptop_id", ASCENDING)])
    db.warranties.create_index([("end_date", ASCENDING)])
    db.warranties.create_index([("customer_name", ASCENDING)])
    print("✅ Created indexes for warranties collection")
    
    # Users indexes
    db.users.create_index([("username", ASCENDING)], unique=True)
    print("✅ Created indexes for users collection")
    
    # Create default admin user if it doesn't exist
    print("\n🔄 Creating default admin user...")
    existing_admin = db.users.find_one({"username": "admin"})
    
    if not existing_admin:
        admin_user = {
            "username": "admin",
            "password": generate_password_hash("admin123"),
            "role": "admin",
            "created_at": datetime.now()
        }
        db.users.insert_one(admin_user)
        print("✅ Created default admin user (username: admin, password: admin123)")
        print("⚠️  IMPORTANT: Change the default password in production!")
    else:
        print("ℹ️  Admin user already exists")
    
    # Display database statistics
    print("\n📊 Database Statistics:")
    print(f"   Laptops: {db.laptops.count_documents({})}")
    print(f"   Spare Parts: {db.spare_parts.count_documents({})}")
    print(f"   Orders: {db.orders.count_documents({})}")
    print(f"   Warranties: {db.warranties.count_documents({})}")
    print(f"   Users: {db.users.count_documents({})}")
    
    print("\n✅ Database initialization complete!")
    print(f"🌐 MongoDB URI: {MONGODB_URI}")
    print(f"📦 Database: {db_name}")
    
    client.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  MongoDB Laptop Inventory - Database Initialization")
    print("=" * 60)
    print()
    
    init_database()
