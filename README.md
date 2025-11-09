# MongoDB Laptop Inventory Management System

A modern web-based laptop inventory management system built with Flask and MongoDB. This application provides comprehensive tools for managing laptop inventory, spare parts, customer orders, and warranties.

## 🚀 Features

### Core Functionality
- **MongoDB Integration**: Modern NoSQL database for flexible data storage
- **Dual Access Modes**: Guest shopping interface and admin management panel
- **Image Management**: Base64 image storage directly in MongoDB
- **Smart Serial Numbers**: Auto-generated serial numbers based on brand and date

### Inventory Management
- **Laptop Tracking**: Complete laptop lifecycle from purchase to sale
- **Spare Parts System**: RAM and storage parts with pricing
- **Bulk Operations**: Multi-select for batch operations
- **Status Tracking**: Available, sold, reserved, etc.

### Customer Features
- **Guest Shopping**: Browse laptops without login required
- **Laptop Customization**: Add spare parts upgrades with real-time pricing
- **Shopping Cart**: Multi-laptop cart with customizations
- **Order Tracking**: Check order status by email and order ID

### Admin Features
- **Dashboard**: Real-time statistics and recent activity
- **Order Management**: Process orders through workflow (unconfirmed → confirmed → in progress → completed)
- **Warranty Tracking**: Color-coded warranty countdown timers
- **User Management**: Admin authentication system

## 🛠 Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB with PyMongo
- **Frontend**: HTML5, CSS3, JavaScript (no heavy frameworks)
- **Containerization**: Docker & Docker Compose
- **Image Storage**: Base64 encoding in MongoDB

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd lim-mongodb
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Open http://localhost:5000 in your browser
   - Default admin login: `admin` / `admin123`

### Manual Installation (Development)

1. **Install MongoDB**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mongodb

   # macOS
   brew install mongodb
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export MONGODB_URI="mongodb://localhost:27017/laptop_inventory"
   export SECRET_KEY="your-secret-key"
   ```

4. **Run the application**
   ```bash
   cd app
   python __init__.py
   ```

## 📊 Database Schema

### Collections Structure

**Laptops Collection**
```javascript
{
  _id: ObjectId,
  serial_number: "DE11070101",
  brand: "Dell",
  model: "Latitude 7420",
  cpu: "Intel i7-1185G7",
  ram: "16GB DDR4",
  storage: "512GB NVMe SSD",
  os: "Windows 11 Pro",
  condition: "Excellent",
  purchase_price: 800.00,
  selling_price: 1200.00,
  date_purchased: ISODate,
  date_sold: ISODate,
  status: "available", // available, sold, reserved
  description: "...",
  image: "base64_encoded_string",
  image_filename: "laptop.jpg",
  created_at: ISODate,
  updated_at: ISODate
}
```

**Spare Parts Collection**
```javascript
{
  _id: ObjectId,
  name: "Corsair Vengeance 16GB DDR4",
  type: "RAM", // RAM, Storage
  price: 89.99,
  quantity: 5,
  description: "...",
  created_at: ISODate
}
```

**Orders Collection**
```javascript
{
  _id: ObjectId,
  order_id: "ORD000001",
  customer_name: "John Doe",
  email: "john@example.com",
  phone: "+1234567890",
  address: "123 Main St, City, State",
  status: "unconfirmed", // unconfirmed, confirmed, in_progress, completed
  items: [
    {
      laptop_id: ObjectId,
      laptop_brand: "Dell",
      laptop_model: "Latitude 7420",
      base_price: 1200.00,
      spare_parts: [
        {
          part_id: ObjectId,
          name: "32GB RAM Upgrade",
          price: 150.00
        }
      ],
      total_price: 1350.00
    }
  ],
  total_amount: 1350.00,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Warranties Collection**
```javascript
{
  _id: ObjectId,
  laptop_id: ObjectId,
  customer_name: "John Doe",
  start_date: ISODate,
  end_date: ISODate,
  duration_months: 12,
  description: "Standard warranty",
  created_at: ISODate
}
```

**Users Collection**
```javascript
{
  _id: ObjectId,
  username: "admin",
  password: "hashed_password",
  role: "admin",
  created_at: ISODate
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
MONGODB_URI=mongodb://localhost:27017/laptop_inventory
SECRET_KEY=your-very-secret-key-here
FLASK_ENV=development
PORT=5000
```

### MongoDB Indexes

The application automatically creates indexes for:
- Laptop serial numbers (unique)
- Laptop status and brand
- Order IDs and email addresses
- Warranty laptop IDs and end dates
- Spare parts name and type

## 🎯 Usage Guide

### Admin Workflow

1. **Login**: Use admin credentials to access management features
2. **Add Laptops**: Upload laptop details with images
3. **Manage Spare Parts**: Add RAM and storage upgrades with pricing
4. **Process Orders**: Move orders through confirmation workflow
5. **Track Warranties**: Monitor warranty expiration dates

### Customer Workflow

1. **Browse Shop**: View available laptops without login
2. **Customize Laptop**: Select upgrades and see price changes
3. **Add to Cart**: Build cart with multiple customized laptops
4. **Checkout**: Provide details and place order
5. **Track Order**: Check status using email and order ID

## 🚀 Deployment

### Production Deployment

1. **Update Docker Compose for production**
   ```yaml
   # Add to docker-compose.yml
   environment:
     - FLASK_ENV=production
     - MONGODB_URI=mongodb://mongodb:27017/laptop_inventory
   ```

2. **Use external MongoDB (recommended)**
   ```bash
   # Update MONGODB_URI to point to MongoDB Atlas or external instance
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/laptop_inventory
   ```

3. **Enable authentication**
   ```yaml
   # Add to MongoDB service
   environment:
     MONGO_INITDB_ROOT_USERNAME: admin
     MONGO_INITDB_ROOT_PASSWORD: strongpassword
   ```

### Security Considerations

- Change default admin credentials
- Use strong SECRET_KEY
- Enable MongoDB authentication
- Use HTTPS in production
- Regular database backups

## 🔄 Migration from SQLite Version

If migrating from the SQLite version:

1. **Export data from SQLite**
2. **Transform data structure for MongoDB**
3. **Import using MongoDB tools**
4. **Update image storage format**

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Built by Edgar Effendi in 2025.

---

**Ready to modernize your laptop inventory management with MongoDB? Get started today!**