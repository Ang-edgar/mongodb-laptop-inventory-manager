# MongoDB Laptop Inventory Manager

A web-based inventory management system for laptop repair shops and resellers. Built with Flask and MongoDB.

## Features

### For Customers
- Browse available laptops without needing an account
- Customize laptops with spare parts (RAM, storage upgrades)
- Shopping cart with real-time pricing
- Order tracking by email and order ID

### For Admins
- Dashboard with inventory stats
- Add and edit laptop listings with images
- Manage spare parts inventory
- Process orders through workflow stages
- Track warranties with expiration dates

### Technical
- MongoDB backend for flexible schema
- Base64 image storage
- Auto-generated serial numbers
- Session-based shopping cart
- Simple authentication system

## Tech Stack

- Backend: Flask + PyMongo
- Database: MongoDB
- Frontend: HTML/CSS/JavaScript with Bootstrap
- Deployment: Docker + Docker Compose

## Installation

### Quick Start (Docker)

**Prerequisites:** Docker and Docker Compose installed

1. Clone the repo
   ```bash
   git clone https://github.com/Ang-edgar/mongodb-laptop-inventory-manager.git
   cd mongodb-laptop-inventory-manager
   ```

2. Copy environment template
   ```bash
   cp .env.example .env
   ```

3. Start containers
   ```bash
   docker-compose up -d
   ```

4. Initialize database
   ```bash
   docker-compose exec web python scripts/init_db.py
   ```

5. Open http://localhost:5000
   - Default login: `admin` / `admin123` (change this!)

### Alternative: Run setup script
```bash
./setup.sh
```
The script will guide you through Docker or manual setup.

### Manual Setup (No Docker)

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

3. Setup Python environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Configure environment
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Initialize database
   ```bash
   python scripts/init_db.py
   ```

6. Run application
   ```bash
   cd app
   python __init__.py
   ```

Application runs on http://localhost:5000

## Database Schema

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

The database auto-creates indexes for serial numbers, order IDs, and email lookups.

## Configuration

Copy `.env.example` to `.env` and update:

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/laptop_inventory
# For Atlas cloud: mongodb+srv://user:pass@cluster.mongodb.net/laptop_inventory

# Flask
SECRET_KEY=generate-random-key-here
FLASK_ENV=development
PORT=5000

# Default admin (change these!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

Generate a secure SECRET_KEY:
```bash
openssl rand -hex 32
```

## Usage

### As a Customer
1. Browse available laptops at `/shop`
2. Click laptop to view details and add spare parts
3. Add to cart and checkout
4. Track order at `/track-order` with email and order ID

### As Admin
1. Login at `/admin` (default: admin/admin123)
2. Add laptops with images and specs
3. Manage spare parts inventory
4. Process orders: unconfirmed → confirmed → in progress → completed
5. Track warranties

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides on:
- VPS deployment (DigitalOcean, Linode, AWS)
- MongoDB Atlas cloud setup
- Raspberry Pi installation
- Production security checklist
- Backup strategies

### Quick Production Notes

For production use:
- Change default admin password
- Generate strong SECRET_KEY
- Use MongoDB Atlas or enable authentication
- Setup HTTPS with Nginx/Caddy
- Configure regular backups

Example production docker-compose:
```yaml
environment:
  - FLASK_ENV=production
  - MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/db
```

## Troubleshooting

**MongoDB connection issues:**
```bash
docker-compose logs mongodb
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

**Application errors:**
```bash
docker-compose logs web
docker-compose restart web
```

**Port 5000 already in use:**
```bash
sudo lsof -i :5000
# Or change PORT in .env
```

## Project Structure

```
mongodb-laptop-inventory-manager/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models/
│   │   └── database.py       # MongoDB models
│   ├── routes/
│   │   ├── main.py           # Homepage
│   │   ├── admin.py          # Admin panel routes
│   │   ├── auth.py           # Authentication
│   │   └── guest.py          # Shop, cart, checkout
│   └── templates/            # Jinja2 templates
├── scripts/
│   └── init_db.py           # Database initialization
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

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
- Repository: [mongodb-laptop-inventory-manager](https://github.com/Ang-edgar/mongodb-laptop-inventory-manager)

---

**Ready to modernize your laptop inventory management with MongoDB? Get started today!** 🚀