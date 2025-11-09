# Quick Start Guide

Get the laptop inventory system running in 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- Git installed
- 2GB free RAM

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Ang-edgar/mongodb-laptop-inventory-manager.git
cd mongodb-laptop-inventory-manager
```

### 2. Start the Services

```bash
docker-compose -f docker-compose-microservices.yml up -d
```

This starts:
- MongoDB (port 27017)
- Admin Backend (port 5000)
- Guest Frontend (port 5001)

### 3. Verify Services

```bash
# Check all containers are running
docker ps

# Test admin API
curl http://localhost:5000/api/health

# Test guest app
curl http://localhost:5001
```

## First Steps

### For Customers

1. **Register an Account**
   - Open http://localhost:5001/register
   - Enter your name, email, and password
   - Click "Create Account"

2. **Browse Products**
   - Go to http://localhost:5001/shop
   - View available laptops
   - Click on any laptop for details

3. **Add to Cart**
   - On laptop detail page, add spare parts if desired
   - Click "Add to Cart"
   - View cart at http://localhost:5001/cart

4. **Checkout**
   - Click "Proceed to Checkout"
   - Fill in delivery information
   - Complete your order

### For Administrators

1. **Access Admin Panel**
   - Open http://localhost:5000/admin
   - Login with:
     - Username: `admin`
     - Password: `admin123`
   - **⚠️ Change these credentials immediately!**

2. **Add Your First Laptop**
   - Click "Add Laptop" in the admin panel
   - Fill in the details:
     - Brand: Dell
     - Model: Latitude 7420
     - CPU: Intel i7
     - RAM: 16GB
     - Storage: 512GB SSD
     - Price: 1200
   - Upload an image
   - Click "Save"

3. **Add Spare Parts**
   - Go to "Spare Parts" section
   - Add items like:
     - 32GB RAM Upgrade ($150)
     - 1TB SSD Upgrade ($200)
     - Laptop Bag ($50)

4. **Manage Orders**
   - View customer orders in "Orders" section
   - Update order status:
     - Unconfirmed → Confirmed → In Progress → Completed

## Configuration

### Change Admin Password

```bash
# Edit .env file in project root
nano .env

# Update these lines:
ADMIN_USERNAME=your-username
ADMIN_PASSWORD=your-secure-password

# Restart admin container
docker-compose -f docker-compose-microservices.yml restart admin
```

### Change JWT Secret

```bash
# Generate a secure secret
openssl rand -hex 32

# Edit guest-app/.env
nano guest-app/.env

# Update this line:
JWT_SECRET=your-generated-secret-here

# Restart guest container
docker-compose -f docker-compose-microservices.yml restart guest
```

## Testing

### Test User Registration

```bash
curl -X POST http://localhost:5001/register \
  -d "name=John Doe" \
  -d "email=john@example.com" \
  -d "password=password123" \
  -d "confirm_password=password123"
```

### Test User Login

```bash
curl -X POST http://localhost:5001/login \
  -d "email=john@example.com" \
  -d "password=password123" \
  -c cookies.txt
```

### Test API

```bash
# Get all laptops
curl http://localhost:5000/api/laptops

# Get specific laptop (replace ID)
curl http://localhost:5000/api/laptops/507f1f77bcf86cd799439011

# Health check
curl http://localhost:5000/api/health
```

## Common Commands

### View Logs

```bash
# All services
docker-compose -f docker-compose-microservices.yml logs -f

# Specific service
docker-compose -f docker-compose-microservices.yml logs -f guest
docker-compose -f docker-compose-microservices.yml logs -f admin
docker-compose -f docker-compose-microservices.yml logs -f mongodb
```

### Restart Services

```bash
# Restart all
docker-compose -f docker-compose-microservices.yml restart

# Restart specific service
docker-compose -f docker-compose-microservices.yml restart guest
```

### Stop Services

```bash
# Stop all containers
docker-compose -f docker-compose-microservices.yml down

# Stop and remove volumes (fresh start)
docker-compose -f docker-compose-microservices.yml down -v
```

### Rebuild After Code Changes

```bash
# Rebuild all services
docker-compose -f docker-compose-microservices.yml up -d --build

# Rebuild specific service
docker-compose -f docker-compose-microservices.yml up -d --build guest
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000 or 5001
sudo lsof -i :5000
sudo lsof -i :5001

# Kill the process
sudo kill -9 <PID>
```

### MongoDB Connection Error

```bash
# Check MongoDB is running
docker exec lim_mongodb mongosh --eval "db.adminCommand('ping')"

# Check MongoDB logs
docker logs lim_mongodb
```

### Authentication Not Working

```bash
# Rebuild guest container (installs JWT dependencies)
docker-compose -f docker-compose-microservices.yml up -d --build guest

# Check if JWT packages are installed
docker exec lim_guest pip list | grep -i jwt
docker exec lim_guest pip list | grep -i bcrypt
```

### Guest App Can't Connect to Admin

```bash
# Check admin API is running
curl http://localhost:5000/api/health

# Check guest logs
docker logs lim_guest

# Verify ADMIN_API_URL in guest-app/.env
docker exec lim_guest env | grep ADMIN_API_URL
```

## Next Steps

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- VPS deployment
- MongoDB Atlas setup
- HTTPS configuration
- Security hardening

### Kubernetes Deployment

See [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md) for:
- Kubernetes manifests
- Horizontal pod autoscaling
- Multi-region deployment
- Load balancing

### Customization

See [MICROSERVICES.md](MICROSERVICES.md) for:
- API integration
- Adding features
- Scaling strategies
- Multi-location deployment

## Support

### Documentation
- [README.md](README.md) - Project overview
- [MICROSERVICES.md](MICROSERVICES.md) - Architecture
- [AUTHENTICATION.md](docs/AUTHENTICATION.md) - Auth system
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [CHANGELOG.md](CHANGELOG.md) - Version history

### Get Help
- GitHub Issues: https://github.com/Ang-edgar/mongodb-laptop-inventory-manager/issues
- Email: edgarwineffendi@gmail.com

## Success Checklist

- [ ] All containers running (`docker ps` shows 3 containers)
- [ ] Admin panel accessible at http://localhost:5000/admin
- [ ] Guest app accessible at http://localhost:5001
- [ ] API health check returns success
- [ ] Can register a new user
- [ ] Can login with registered user
- [ ] Can add laptop to cart
- [ ] Admin can add laptops and spare parts
- [ ] Changed default admin password
- [ ] Generated secure JWT_SECRET

**Congratulations! Your laptop inventory system is ready!** 🎉

## Quick Architecture Overview

```
Customer Flow:
1. Visit http://localhost:5001
2. Register account (JWT token issued)
3. Browse laptops (API call to admin)
4. Add to cart (session storage)
5. Checkout (order saved to MongoDB)

Admin Flow:
1. Visit http://localhost:5000/admin
2. Login as admin
3. Add/edit laptops (saved to MongoDB)
4. Manage orders (update status)
5. Track warranties

Behind the Scenes:
- Guest app → calls → Admin API → MongoDB
- JWT authentication (stateless, scalable)
- REST API with CORS
- Docker containerized
- Ready for Kubernetes
```

**Happy selling!** 🚀
