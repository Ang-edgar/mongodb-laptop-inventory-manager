# MongoDB Laptop Inventory Manager

A modern, cloud-native inventory management system for laptop repair shops and resellers. Built with microservices architecture using Flask, MongoDB, and JWT authentication.

## Features

### For Customers
- User registration and authentication (JWT-based)
- Browse laptops with personalized experience
- Customize laptops with spare parts (RAM, storage upgrades)
- Shopping cart with real-time pricing
- Order tracking and history
- Secure account management

### For Admins
- Dashboard with inventory stats
- Full REST API for remote management
- Add and edit laptop listings with images
- Manage spare parts inventory
- Process orders through workflow stages
- Track warranties with expiration dates

### Technical
- **Microservices architecture** with separate admin and guest apps
- **JWT authentication** for stateless, Kubernetes-ready auth
- **REST API** with CORS support for distributed deployments
- **MongoDB backend** for flexible schema
- **bcrypt password hashing** for security
- **Session-based shopping cart** with persistent authentication
- **Scalable design** ready for horizontal scaling

## Tech Stack

- **Backend**: Flask 2.3.3 + PyMongo 4.6.0
- **Database**: MongoDB 7.0
- **Authentication**: JWT (PyJWT 2.8.0) + bcrypt 4.1.2
- **Architecture**: Microservices (Admin API + Guest Frontend)
- **Frontend**: HTML/CSS/JavaScript with Bootstrap 5
- **API**: REST with CORS support
- **Deployment**: Docker + Docker Compose, Kubernetes-ready

## Installation

### Architecture Overview

This system uses a **microservices architecture**:
- **Admin Backend** (Port 5000): REST API + admin panel + MongoDB
- **Guest Frontend** (Port 5001): Customer-facing storefront with authentication

See [MICROSERVICES.md](MICROSERVICES.md) for detailed architecture documentation.

### Quick Start (Docker - Microservices)

**Prerequisites:** Docker and Docker Compose installed

1. Clone the repo
   ```bash
   git clone https://github.com/Ang-edgar/mongodb-laptop-inventory-manager.git
   cd mongodb-laptop-inventory-manager
   ```

2. Start all services
   ```bash
   docker-compose -f docker-compose-microservices.yml up -d
   ```

3. Access the applications:
   - **Guest storefront**: http://localhost:5001 (register/login as customer)
   - **Admin panel**: http://localhost:5000/admin (admin/admin123)
   - **API documentation**: http://localhost:5000/api/health

4. Create your first customer account:
   - Go to http://localhost:5001/register
   - Sign up with email and password
   - Start shopping!

### Alternative: Monolithic Deployment (Legacy)

For a single-server deployment with everything bundled together:

```bash
docker-compose up -d
```

This runs the original monolithic version on port 5000.

### Manual Setup (Development)

**Prerequisites:** Python 3.10+, MongoDB 5.0+

1. Clone and enter directory
   ```bash
   git clone https://github.com/Ang-edgar/mongodb-laptop-inventory-manager.git
   cd mongodb-laptop-inventory-manager
   ```

2. Install MongoDB if needed
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mongodb
   
   # macOS
   brew install mongodb-community
   brew services start mongodb-community
   ```

3. Setup Admin Backend
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cd app
   python app.py  # Runs on port 5000
   ```

4. Setup Guest Frontend (in a new terminal)
   ```bash
   cd guest-app
   source ../venv/bin/activate
   pip install -r requirements.txt
   python app.py  # Runs on port 5001
   ```

## Database Schema

### Users Collection (NEW - JWT Authentication)
```javascript
{
  _id: ObjectId,
  email: "customer@example.com",
  password: "$2b$12$hashed_password",  // bcrypt hashed
  name: "John Doe",
  created_at: ISODate,
  is_active: true
}
```
**Index**: `email` (unique)

### Laptops Collection
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
  status: "available",
  description: "...",
  image: "base64_string",
  created_at: ISODate,
  updated_at: ISODate
}
```

### Orders Collection
```javascript
{
  _id: ObjectId,
  order_id: "ORD000001",
  user_id: ObjectId,  // NEW - links to users collection
  customer_name: "John Doe",
  email: "john@example.com",
  phone: "+1234567890",
  address: "123 Main St",
  status: "unconfirmed",
  items: [
    {
      laptop_id: ObjectId,
      laptop_brand: "Dell",
      laptop_model: "Latitude 7420",
      base_price: 1200.00,
      spare_parts: [{part_id: ObjectId, name: "32GB RAM", price: 150.00}],
      total_price: 1350.00
    }
  ],
  total_amount: 1350.00,
  created_at: ISODate
}
```

The database auto-creates indexes for serial numbers, order IDs, email lookups, and user authentication.

## Configuration

### Admin Backend (.env)

```env
# MongoDB
MONGODB_URI=mongodb://mongodb:27017/laptop_inventory
# For Atlas cloud: mongodb+srv://user:pass@cluster.mongodb.net/laptop_inventory

# Flask
SECRET_KEY=generate-random-key-here
FLASK_ENV=development
PORT=5000

# Default admin credentials (change these!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### Guest Frontend (.env)

```env
# Admin API connection
ADMIN_API_URL=http://localhost:5000/api
# For production: https://your-admin-server.com/api

# JWT Authentication
JWT_SECRET=your-jwt-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24

# Flask
SECRET_KEY=guest-app-secret-key
FLASK_ENV=development
PORT=5001

# MongoDB (for user authentication)
MONGODB_URI=mongodb://mongodb:27017/laptop_inventory
```

Generate secure keys:
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET (use a different value)
openssl rand -hex 32
```

**Important**: Use different `JWT_SECRET` values in production!

## Usage

### As a Customer (Guest App)

1. **Register an account**
   - Visit http://localhost:5001/register
   - Create account with email and password
   - Secure JWT authentication

2. **Browse and shop**
   - Browse laptops at http://localhost:5001/shop
   - Click laptop to view details
   - Add spare parts for customization
   - Add to cart

3. **Checkout**
   - Review cart at `/cart`
   - Proceed to checkout
   - Fill in delivery details
   - Complete order

4. **Track orders**
   - View order history in user dropdown
   - Track order status
   - All orders linked to your account

### As Admin

1. Login at http://localhost:5000/admin
   - Default: admin/admin123 (change this!)

2. **Manage inventory**
   - Add laptops with specs and images
   - Upload photos (base64 encoded)
   - Set pricing and availability

3. **Manage spare parts**
   - Add RAM, storage, accessories
   - Set prices and stock levels

4. **Process orders**
   - View all customer orders
   - Update status: unconfirmed → confirmed → in progress → completed
   - View customer details

5. **Track warranties**
   - Add warranty information
   - Monitor expiration dates

## Deployment

See detailed deployment guides:
- [DEPLOYMENT.md](DEPLOYMENT.md) - VPS, MongoDB Atlas, Production setup
- [MICROSERVICES.md](MICROSERVICES.md) - Distributed deployment, scaling
- [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md) - JWT auth system, Kubernetes

### Quick Production Notes

**For production deployment:**
1. Change all default passwords (admin + JWT secrets)
2. Generate strong `SECRET_KEY` and `JWT_SECRET`
3. Use MongoDB Atlas or enable authentication
4. Setup HTTPS with Nginx/Caddy
5. Configure regular backups
6. Set `FLASK_ENV=production`
7. Use proper CORS origins (not wildcard)

**Kubernetes Ready:**
The JWT authentication is stateless and requires no session affinity. Deploy multiple guest app replicas without any special configuration. See [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md) for Kubernetes manifests.

### Scaling Options

1. **Single Location**: Run all services on one server
2. **Multiple Storefronts**: Deploy guest apps in different regions, all connecting to central admin API
3. **Kubernetes**: Horizontal pod autoscaling with stateless JWT auth
4. **Edge Deployment**: Deploy guest apps on edge locations for better performance

Example multi-region:
```yaml
# Admin Backend (us-east)
admin.example.com:5000

# Guest Apps (multiple regions)
us.shop.example.com  → connects to admin.example.com/api
eu.shop.example.com  → connects to admin.example.com/api
asia.shop.example.com → connects to admin.example.com/api
```

## Troubleshooting

**MongoDB connection issues:**
```bash
docker-compose -f docker-compose-microservices.yml logs mongodb
docker exec lim_mongodb mongosh --eval "db.adminCommand('ping')"
```

**Admin API not responding:**
```bash
docker-compose -f docker-compose-microservices.yml logs admin
curl http://localhost:5000/api/health
```

**Guest app can't connect to API:**
```bash
# Check ADMIN_API_URL in guest-app/.env
docker-compose -f docker-compose-microservices.yml logs guest
```

**Authentication not working:**
```bash
# Rebuild guest container after adding JWT dependencies
docker-compose -f docker-compose-microservices.yml up -d --build guest

# Check JWT_SECRET is set
docker exec lim_guest env | grep JWT
```

**Port conflicts:**
```bash
sudo lsof -i :5000
sudo lsof -i :5001
# Kill process or change PORT in .env
```

## Project Structure

```
mongodb-laptop-inventory-manager/
├── app/                          # Admin Backend
│   ├── app.py                   # Main Flask app
│   ├── database.py              # MongoDB models
│   ├── routes/
│   │   ├── api.py              # REST API endpoints
│   │   ├── admin.py            # Admin panel routes
│   │   └── auth.py             # Admin authentication
│   └── templates/              # Admin templates
├── guest-app/                   # Guest Frontend
│   ├── app.py                  # Guest Flask app
│   ├── auth.py                 # JWT authentication
│   ├── templates/              # Customer templates
│   │   ├── login.html         # User login
│   │   ├── register.html      # User registration
│   │   ├── shop.html          # Product listing
│   │   └── cart.html          # Shopping cart
│   └── requirements.txt        # Guest dependencies
├── docs/
│   └── AUTHENTICATION.md       # JWT auth documentation
├── docker-compose-microservices.yml  # Microservices setup
├── docker-compose.yml          # Legacy monolithic setup
├── MICROSERVICES.md            # Architecture guide
├── DEPLOYMENT.md               # Deployment guide
└── README.md
```

## API Documentation

### REST API Endpoints

The admin backend exposes a RESTful API at `http://localhost:5000/api`:

**Laptops**
- `GET /api/laptops` - List all available laptops
- `GET /api/laptops/<id>` - Get laptop by ID

**Spare Parts**
- `GET /api/spare-parts` - List all spare parts
- `GET /api/spare-parts/<id>` - Get spare part by ID

**Orders**
- `POST /api/orders` - Create new order
- `GET /api/orders/<order_id>` - Get order by order ID
- `GET /api/orders/lookup?email=...&order_id=...` - Lookup order

**Health Check**
- `GET /api/health` - API status

All API endpoints return JSON and support CORS for cross-origin requests.

See [MICROSERVICES.md](MICROSERVICES.md) for API usage examples.

## Contributing

Fork the repo, make changes, and submit a pull request.

## License

MIT License - see LICENSE file

## Author

Edgar - [@Ang-edgar](https://github.com/Ang-edgar)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## � Acknowledgments

- Flask framework
- MongoDB and PyMongo
- Bootstrap for UI components

## �👨‍💻 Author

Built by **Edgar Effendi** in 2025.

## 📧 Contact

- GitHub: [@Ang-edgar](https://github.com/Ang-edgar)
- Email: edgarwineffendi@gmail.com

---

**Ready to modernize your laptop inventory management with MongoDB? Get started today!** 🚀