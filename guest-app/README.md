# Guest Storefront Application

Standalone customer-facing application with JWT authentication that connects to the admin API.

## Overview

This is a lightweight Flask application for customers to browse products, manage accounts, and place orders. It features JWT-based authentication for secure, stateless user management that works perfectly with Kubernetes deployments. Multiple instances can be deployed in different locations while connecting to one centralized admin backend.

## Features

- **User Authentication**: JWT-based registration and login
- **Product Browsing**: Browse laptops from admin inventory
- **Product Customization**: View details and add spare parts
- **Shopping Cart**: Session-based cart management
- **Order Management**: Checkout and order tracking
- **Secure & Scalable**: Stateless auth, no session affinity required

## Technology Stack

- **Flask 2.3.3**: Web framework
- **PyJWT 2.8.0**: JWT token generation and validation
- **bcrypt 4.1.2**: Secure password hashing
- **PyMongo 4.6.0**: MongoDB driver for user storage
- **requests**: HTTP client for admin API communication

## Configuration

1. Copy environment template:
```bash
cp .env.example .env
```

2. Update configuration in `.env`:
```env
# Admin API Connection
ADMIN_API_URL=http://localhost:5000/api
# For production: https://your-admin-server.com/api

# JWT Authentication
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24

# Flask Configuration
SECRET_KEY=another-secret-key
FLASK_ENV=development
PORT=5001

# MongoDB Connection (for user authentication)
MONGODB_URI=mongodb://mongodb:27017/laptop_inventory
# For Atlas: mongodb+srv://user:pass@cluster.mongodb.net/laptop_inventory
```

**Important**: Use strong, unique values for `JWT_SECRET` and `SECRET_KEY` in production!

## Running Locally

### With Docker (Recommended)
```bash
# From project root
docker-compose -f docker-compose-microservices.yml up -d guest
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Access at http://localhost:5001

## Authentication System

### User Registration
- Navigate to `/register`
- Create account with name, email, password
- Passwords are hashed with bcrypt (cost factor 12)
- JWT token automatically set in httpOnly cookie
- Redirected to shop after successful registration

### User Login
- Navigate to `/login`
- Authenticate with email and password
- JWT token set in secure httpOnly cookie
- 24-hour expiration (configurable)
- Redirected to shop after successful login

### Session Management
- JWT tokens stored in httpOnly cookies (XSS protection)
- Tokens automatically included in requests
- No server-side session storage needed
- Works across multiple server instances

### Logout
- Click logout in user dropdown
- JWT cookie cleared
- Redirected to homepage

## Deployment

### Single Instance
```bash
docker build -t guest-app .
docker run -p 5001:5001 \
  -e ADMIN_API_URL=http://admin-server/api \
  -e JWT_SECRET=your-secret \
  -e MONGODB_URI=mongodb://mongodb:27017/laptop_inventory \
  guest-app
```

### Multiple Instances (Load Balanced)
```bash
# Instance 1 (us-east)
docker run -d -p 5001:5001 \
  -e ADMIN_API_URL=https://admin.example.com/api \
  -e JWT_SECRET=shared-secret \
  guest-app

# Instance 2 (eu-west)
docker run -d -p 5001:5001 \
  -e ADMIN_API_URL=https://admin.example.com/api \
  -e JWT_SECRET=shared-secret \
  guest-app

# Instance 3 (ap-south)
docker run -d -p 5001:5001 \
  -e ADMIN_API_URL=https://admin.example.com/api \
  -e JWT_SECRET=shared-secret \
  guest-app
```

**Note**: All instances must use the same `JWT_SECRET` to validate tokens across instances.

### Kubernetes Deployment

The stateless JWT authentication makes this app perfect for Kubernetes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: guest-app
spec:
  replicas: 3  # Scale as needed
  selector:
    matchLabels:
      app: guest-app
  template:
    metadata:
      labels:
        app: guest-app
    spec:
      containers:
      - name: guest
        image: your-registry/guest-app:latest
        ports:
        - containerPort: 5001
        env:
        - name: ADMIN_API_URL
          value: "http://admin-api-service:5000/api"
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: auth-secrets
              key: jwt-secret
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: mongodb-uri
---
apiVersion: v1
kind: Service
metadata:
  name: guest-app-service
spec:
  selector:
    app: guest-app
  ports:
  - port: 80
    targetPort: 5001
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: guest-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: guest-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Cloud Platforms

**Heroku**:
```bash
heroku create my-laptop-shop
heroku config:set ADMIN_API_URL=https://admin.example.com/api
heroku config:set JWT_SECRET=$(openssl rand -hex 32)
git push heroku main
```

**Railway**:
```bash
railway init
railway add
# Set environment variables in Railway dashboard
railway up
```

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Guest App #1   │      │  Guest App #2   │      │  Guest App #3   │
│  (Port 5001)    │      │  (Port 5002)    │      │  (Port 5003)    │
│  Location: NYC  │      │  Location: LA   │      │  Location: EU   │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │ HTTP API Calls
                                  ▼
                         ┌─────────────────┐
                         │  Admin Backend  │
                         │   (Port 5000)   │
                         │  - API Endpoints│
                         │  - Admin Panel  │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    MongoDB      │
                         │  (Port 27017)   │
                         │  - Inventory    │
                         │  - Users        │
                         │  - Orders       │
                         └─────────────────┘
```

Multiple guest frontends share one centralized backend and database.

## Security Features

### Authentication Security
- **bcrypt hashing**: Passwords hashed with cost factor 12
- **JWT signing**: Tokens signed with HS256 algorithm
- **httpOnly cookies**: Prevents XSS attacks
- **Token expiration**: Automatic 24-hour expiration
- **Email uniqueness**: Enforced by MongoDB unique index

### Best Practices
1. Use strong `JWT_SECRET` (minimum 32 characters)
2. Enable HTTPS in production
3. Set `samesite='Strict'` for cookies over HTTPS
4. Rotate JWT secrets periodically
5. Monitor failed login attempts
6. Implement rate limiting for auth endpoints

### Production Checklist
- [ ] Generate strong JWT_SECRET: `openssl rand -hex 32`
- [ ] Enable HTTPS/TLS
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Enable MongoDB authentication
- [ ] Use environment variables (never hardcode secrets)
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Test authentication flows

## API Integration

The guest app calls these admin API endpoints:

### Products
- `GET /api/laptops` - List all laptops
- `GET /api/laptops/<id>` - Get laptop details
- `GET /api/spare-parts` - List spare parts
- `GET /api/spare-parts/<id>` - Get spare part details

### Orders
- `POST /api/orders` - Create new order
- `GET /api/orders/<order_id>` - Get order details
- `GET /api/orders/lookup` - Track order by email

### Health Check
- `GET /api/health` - Check API status

All requests include proper error handling and timeout configuration.

## Troubleshooting

### Cannot connect to admin API
```bash
# Check ADMIN_API_URL
echo $ADMIN_API_URL

# Test API connectivity
curl http://your-admin-server/api/health

# Check firewall rules
# Ensure admin server allows connections from guest app IP
```

### Authentication not working
```bash
# Rebuild container to install JWT dependencies
docker-compose -f docker-compose-microservices.yml up -d --build guest

# Check JWT_SECRET is set
docker exec lim_guest env | grep JWT_SECRET

# Check MongoDB connection
docker exec lim_guest python -c "from pymongo import MongoClient; print(MongoClient('mongodb://mongodb:27017').server_info())"
```

### Users can't login
```bash
# Check MongoDB users collection
docker exec lim_mongodb mongosh laptop_inventory --eval "db.users.find().pretty()"

# Check password hashing
# Passwords should start with $2b$ (bcrypt)

# Check JWT token generation
docker logs lim_guest | grep "JWT"
```

### Session not persisting
- Check browser cookies are enabled
- Verify JWT token in browser DevTools (Application > Cookies)
- Check token expiration time
- Ensure `JWT_SECRET` is consistent across instances

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New Features
1. Update routes in `app.py`
2. Create templates in `templates/`
3. Test locally
4. Deploy with Docker

### Adding Protected Routes
```python
from auth import login_required

@app.route('/protected')
@login_required
def protected_route():
    user = request.current_user
    return f"Hello {user['name']}"
```

## Documentation

- [Main README](../README.md) - Project overview
- [Microservices Guide](../MICROSERVICES.md) - Architecture details
- [Authentication Guide](../docs/AUTHENTICATION.md) - JWT auth deep dive
- [Deployment Guide](../DEPLOYMENT.md) - Production deployment

## Support

For issues and questions:
- GitHub Issues: https://github.com/Ang-edgar/mongodb-laptop-inventory-manager/issues
- Email: edgarwineffendi@gmail.com

---

**Ready to deploy your customer storefront? Get started in minutes!** 🚀
