# Microservices Architecture Guide

## Overview

The laptop inventory system uses a modern microservices architecture with JWT authentication:

1. **Admin Backend** - Centralized server with MongoDB, admin panel, and REST API
2. **Guest Frontend** - Lightweight storefront with user authentication that connects to admin API

This architecture enables:
- Deploy multiple authenticated storefronts in different locations
- All storefronts share the same inventory, orders, and user data
- Scale guest frontends independently with Kubernetes
- Stateless JWT authentication (no session affinity required)
- Deploy guests on edge locations for better performance
- User accounts with secure password storage

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Customer Layer                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │  Guest App #1   │  │  Guest App #2   │  │  Guest App #3   │    │
│  │  (Port 5001)    │  │  (Port 5002)    │  │  (Port 5003)    │    │
│  │  Location: NYC  │  │  Location: LA   │  │  Location: EU   │    │
│  │  - User Login   │  │  - User Login   │  │  - User Login   │    │
│  │  - JWT Auth     │  │  - JWT Auth     │  │  - JWT Auth     │    │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘    │
└───────────┼────────────────────┼────────────────────┼──────────────┘
            │                    │                    │
            └────────────────────┼────────────────────┘
                                 │ REST API Calls + JWT
                                 ▼
            ┌─────────────────────────────────────────┐
            │         Application Layer               │
            │  ┌─────────────────────────────────┐   │
            │  │      Admin Backend API          │   │
            │  │       (Port 5000)               │   │
            │  │  - REST Endpoints (CORS)        │   │
            │  │  - Admin Panel                  │   │
            │  │  - Business Logic               │   │
            │  └────────────┬────────────────────┘   │
            └───────────────┼─────────────────────────┘
                            │
                            ▼
            ┌─────────────────────────────────────────┐
            │          Data Layer                     │
            │  ┌─────────────────────────────────┐   │
            │  │         MongoDB                 │   │
            │  │       (Port 27017)              │   │
            │  │  Collections:                   │   │
            │  │  - laptops (inventory)          │   │
            │  │  - users (JWT auth)             │   │
            │  │  - orders (transactions)        │   │
            │  │  - spare_parts (products)       │   │
            │  │  - warranties (tracking)        │   │
            │  └─────────────────────────────────┘   │
            └─────────────────────────────────────────┘
```

## API Endpoints

The admin backend exposes these REST API endpoints:

### Laptops
- `GET /api/laptops` - List all available laptops
- `GET /api/laptops/<id>` - Get laptop details

### Spare Parts
- `GET /api/spare-parts` - List all spare parts
- `GET /api/spare-parts/<id>` - Get spare part details

### Orders
- `POST /api/orders` - Create new order
- `GET /api/orders/<order_id>` - Get order by order ID
- `GET /api/orders/lookup?email=...&order_id=...` - Lookup order

### Health Check
- `GET /api/health` - Check API status

## Deployment Options

### Option 1: All-in-One (Development)

Run everything on one server:

```bash
docker-compose -f docker-compose-microservices.yml up -d
```

Access:
- Admin: http://localhost:5000
- Guest: http://localhost:5001
- API: http://localhost:5000/api

### Option 2: Separate Servers (Production)

#### Deploy Admin Backend

On your main server (e.g., admin.example.com):

```bash
# Only run admin and MongoDB
docker-compose up -d mongodb admin
```

Update firewall to allow API access:
```bash
ufw allow 5000/tcp
```

#### Deploy Guest Storefront(s)

On separate servers (e.g., store1.example.com, store2.example.com):

```bash
cd guest-app

# Create .env file
cp .env.example .env

# Update ADMIN_API_URL
echo "ADMIN_API_URL=https://admin.example.com/api" >> .env

# Run guest app
docker build -t guest-app .
docker run -d -p 80:5001 --env-file .env guest-app
```

### Option 3: Multiple Guests from Docker Compose

```yaml
# docker-compose.yml (on guest servers)
version: '3.8'
services:
  guest:
    build: ./guest-app
    ports:
      - "80:5001"
    environment:
      - ADMIN_API_URL=https://admin.example.com/api
      - SECRET_KEY=unique-key-per-instance
```

### Option 4: Deploy Guest on Vercel/Netlify

The guest app can also be deployed as a serverless function on platforms like Vercel:

1. Convert Flask routes to serverless functions
2. Point `ADMIN_API_URL` to your admin server
3. Deploy with `vercel deploy`

## Configuration

### Admin Backend (.env)

```env
MONGODB_URI=mongodb://localhost:27017/laptop_inventory
SECRET_KEY=admin-secret-key
FLASK_ENV=production
PORT=5000
```

### Guest Frontend (.env)

```env
ADMIN_API_URL=https://admin.example.com/api
SECRET_KEY=guest-secret-key
FLASK_ENV=production
PORT=5001
```

## Security Considerations

### 1. API Authentication (Optional)

Add API key authentication:

```python
# In admin app
@api.before_request
def check_api_key():
    api_key = request.headers.get('X-API-Key')
    if api_key != os.environ.get('API_KEY'):
        return jsonify({'error': 'Unauthorized'}), 401
```

Update guest app to send API key:

```python
headers = {'X-API-Key': os.environ.get('API_KEY')}
response = requests.get(url, headers=headers)
```

### 2. CORS Configuration

In production, restrict CORS to specific origins:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://store1.example.com",
            "https://store2.example.com"
        ]
    }
})
```

### 3. Rate Limiting

Add rate limiting to API:

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@api.route('/laptops')
@limiter.limit("100 per minute")
def get_laptops():
    ...
```

## Scaling

### Horizontal Scaling

Deploy multiple guest instances behind a load balancer:

```
                    Load Balancer (Nginx)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   Guest #1            Guest #2            Guest #3
```

Nginx config:
```nginx
upstream guest_backend {
    server guest1:5001;
    server guest2:5001;
    server guest3:5001;
}

server {
    location / {
        proxy_pass http://guest_backend;
    }
}
```

### Database Scaling

For high traffic, use MongoDB Atlas with:
- Replica sets for high availability
- Sharding for horizontal scaling
- Read replicas for better performance

## Monitoring

### Health Check

Check if services are running:

```bash
# Admin health
curl http://admin.example.com/api/health

# Expected response
{"success": true, "status": "healthy", "service": "laptop-inventory-admin-api"}
```

### Logging

Centralize logs from all guest instances:

```bash
# In docker-compose
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Backup Strategy

Since all data is centralized in admin backend:

```bash
# Backup MongoDB (on admin server)
docker exec lim_mongodb mongodump --archive=/backup/db-$(date +%Y%m%d).archive --gzip
```

## Troubleshooting

### Guest can't connect to admin API

1. Check if admin API is accessible:
```bash
curl https://admin.example.com/api/health
```

2. Check firewall rules on admin server
3. Verify `ADMIN_API_URL` in guest .env file
4. Check CORS configuration in admin app

### Orders not showing up

1. Check admin MongoDB connection
2. Verify API endpoints are working
3. Check admin logs: `docker logs lim_admin`

### Performance issues

1. Add caching to frequently accessed data
2. Use CDN for guest static assets
3. Deploy guest instances closer to users
4. Optimize MongoDB queries with proper indexes

## Example: Three-Location Deployment

```bash
# Main Server (admin.example.com)
docker-compose up -d mongodb admin

# NYC Server (nyc.example.com)
cd guest-app
ADMIN_API_URL=https://admin.example.com/api docker-compose up -d

# London Server (london.example.com)
cd guest-app
ADMIN_API_URL=https://admin.example.com/api docker-compose up -d

# Tokyo Server (tokyo.example.com)
cd guest-app
ADMIN_API_URL=https://admin.example.com/api docker-compose up -d
```

Now you have one centralized inventory managed from admin.example.com, with three storefronts serving customers in different regions!

## Benefits

✅ Single source of truth for inventory
✅ Easy to deploy new storefronts
✅ Better performance with edge deployment
✅ Independent scaling of frontend and backend
✅ Centralized order management
✅ Lower costs (guest apps are lightweight)
