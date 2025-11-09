# REST API Documentation

Complete RESTful API for the Laptop Inventory Management System.

## Base URL

```
http://localhost:5000/api
```

For production: `https://your-domain.com/api`

## Authentication

Admin operations require authentication via:
- **X-API-Key header**: `X-API-Key: your-api-key`
- **Admin session cookie**: Authenticated admin user

Public endpoints (GET) don't require authentication.

## Response Format

All endpoints return JSON with this structure:

```json
{
  "success": true|false,
  "data": {...},
  "error": "error message if failed"
}
```

## HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Laptops Endpoints

### List Laptops

Get all laptops with optional filtering.

```http
GET /api/laptops
```

**Query Parameters:**
- `status` (optional) - Filter by status: `available`, `sold`, `reserved`
- `brand` (optional) - Filter by brand (case-insensitive partial match)
- `min_price` (optional) - Minimum selling price
- `max_price` (optional) - Maximum selling price

**Example Request:**
```bash
# Get all available laptops
curl http://localhost:5000/api/laptops

# Filter by brand
curl http://localhost:5000/api/laptops?brand=Dell

# Filter by price range
curl http://localhost:5000/api/laptops?min_price=800&max_price=1500
```

**Response:**
```json
{
  "success": true,
  "count": 10,
  "laptops": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "serial_number": "DE11070101",
      "brand": "Dell",
      "model": "Latitude 7420",
      "cpu": "Intel i7-1185G7",
      "ram": "16GB DDR4",
      "storage": "512GB NVMe SSD",
      "os": "Windows 11 Pro",
      "condition": "Excellent",
      "purchase_price": 800.00,
      "selling_price": 1200.00,
      "status": "available",
      "date_purchased": "2025-01-15",
      "description": "...",
      "image": "base64_string",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-20T15:30:00Z"
    }
  ]
}
```

### Get Single Laptop

Get detailed information about a specific laptop.

```http
GET /api/laptops/{laptop_id}
```

**Example:**
```bash
curl http://localhost:5000/api/laptops/507f1f77bcf86cd799439011
```

**Response:**
```json
{
  "success": true,
  "laptop": {
    "_id": "507f1f77bcf86cd799439011",
    "brand": "Dell",
    "model": "Latitude 7420",
    ...
  }
}
```

### Create Laptop

Create a new laptop listing. **Requires admin authentication.**

```http
POST /api/laptops
```

**Headers:**
```
Content-Type: application/json
X-API-Key: your-api-key
```

**Request Body:**
```json
{
  "brand": "Dell",
  "model": "Latitude 7420",
  "cpu": "Intel i7-1185G7",
  "ram": "16GB DDR4",
  "storage": "512GB NVMe SSD",
  "os": "Windows 11 Pro",
  "condition": "Excellent",
  "purchase_price": 800.00,
  "selling_price": 1200.00,
  "status": "available",
  "date_purchased": "2025-01-15",
  "description": "Professional laptop in excellent condition",
  "image": "base64_encoded_image_data"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/laptops \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "brand": "Dell",
    "model": "Latitude 7420",
    "cpu": "Intel i7-1185G7",
    "ram": "16GB DDR4",
    "storage": "512GB NVMe SSD",
    "selling_price": 1200.00
  }'
```

**Response:**
```json
{
  "success": true,
  "laptop_id": "507f1f77bcf86cd799439011",
  "message": "Laptop created successfully"
}
```

### Update Laptop (Full)

Replace all laptop data. **Requires admin authentication.**

```http
PUT /api/laptops/{laptop_id}
```

**Headers:**
```
Content-Type: application/json
X-API-Key: your-api-key
```

**Request Body:** Complete laptop object (all fields)

**Example:**
```bash
curl -X PUT http://localhost:5000/api/laptops/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "brand": "Dell",
    "model": "Latitude 7420",
    "cpu": "Intel i7-1185G7",
    "ram": "32GB DDR4",
    "storage": "1TB NVMe SSD",
    "selling_price": 1500.00,
    "status": "available"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Laptop updated successfully"
}
```

### Update Laptop (Partial)

Update specific fields only. **Requires admin authentication.**

```http
PATCH /api/laptops/{laptop_id}
```

**Headers:**
```
Content-Type: application/json
X-API-Key: your-api-key
```

**Request Body:** Only fields to update

**Example:**
```bash
# Update only the price
curl -X PATCH http://localhost:5000/api/laptops/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "selling_price": 1100.00
  }'

# Update status to sold
curl -X PATCH http://localhost:5000/api/laptops/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "status": "sold",
    "date_sold": "2025-11-09"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Laptop updated successfully"
}
```

### Delete Laptop

Remove a laptop from the system. **Requires admin authentication.**

```http
DELETE /api/laptops/{laptop_id}
```

**Headers:**
```
X-API-Key: your-api-key
```

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/laptops/507f1f77bcf86cd799439011 \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "success": true,
  "message": "Laptop deleted successfully"
}
```

---

## Spare Parts Endpoints

### List Spare Parts

Get all spare parts with optional filtering.

```http
GET /api/spare-parts
```

**Query Parameters:**
- `type` (optional) - Filter by type: `RAM`, `Storage`, etc.

**Example:**
```bash
# Get all spare parts
curl http://localhost:5000/api/spare-parts

# Get only RAM
curl http://localhost:5000/api/spare-parts?type=RAM
```

**Response:**
```json
{
  "success": true,
  "count": 5,
  "spare_parts": [
    {
      "_id": "507f1f77bcf86cd799439012",
      "type": "RAM",
      "brand": "Kingston",
      "capacity": "32GB DDR4",
      "price": 150.00,
      "quantity": 10,
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

### Get Single Spare Part

```http
GET /api/spare-parts/{part_id}
```

**Example:**
```bash
curl http://localhost:5000/api/spare-parts/507f1f77bcf86cd799439012
```

### Create Spare Part

**Requires admin authentication.**

```http
POST /api/spare-parts
```

**Request Body:**
```json
{
  "type": "RAM",
  "brand": "Kingston",
  "capacity": "32GB DDR4",
  "price": 150.00,
  "quantity": 10
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/spare-parts \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "type": "RAM",
    "brand": "Kingston",
    "capacity": "32GB DDR4",
    "price": 150.00,
    "quantity": 10
  }'
```

### Update Spare Part

**Requires admin authentication.**

```http
PUT /api/spare-parts/{part_id}
```

**Example:**
```bash
curl -X PUT http://localhost:5000/api/spare-parts/507f1f77bcf86cd799439012 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "type": "RAM",
    "brand": "Kingston",
    "capacity": "32GB DDR4",
    "price": 140.00,
    "quantity": 15
  }'
```

### Delete Spare Part

**Requires admin authentication.**

```http
DELETE /api/spare-parts/{part_id}
```

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/spare-parts/507f1f77bcf86cd799439012 \
  -H "X-API-Key: your-api-key"
```

---

## Orders Endpoints

### Create Order

Create a new order (public endpoint for customer checkout).

```http
POST /api/orders
```

**Request Body:**
```json
{
  "customer_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, State 12345",
  "items": [
    {
      "laptop_id": "507f1f77bcf86cd799439011",
      "laptop_brand": "Dell",
      "laptop_model": "Latitude 7420",
      "base_price": 1200.00,
      "spare_parts": [
        {
          "part_id": "507f1f77bcf86cd799439012",
          "name": "32GB RAM Upgrade",
          "price": 150.00
        }
      ],
      "total_price": 1350.00
    }
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "address": "123 Main St",
    "items": [{
      "laptop_id": "507f1f77bcf86cd799439011",
      "laptop_brand": "Dell",
      "laptop_model": "Latitude 7420",
      "base_price": 1200.00,
      "total_price": 1200.00
    }]
  }'
```

**Response:**
```json
{
  "success": true,
  "order_id": "ORD000001",
  "message": "Order created successfully"
}
```

### Get Order

Get order details by order ID.

```http
GET /api/orders/{order_id}
```

**Example:**
```bash
curl http://localhost:5000/api/orders/ORD000001
```

**Response:**
```json
{
  "success": true,
  "order": {
    "_id": "507f1f77bcf86cd799439013",
    "order_id": "ORD000001",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "+1234567890",
    "delivery_address": "123 Main St",
    "status": "unconfirmed",
    "items": [...],
    "total_amount": 1350.00,
    "created_at": "2025-11-09T10:00:00Z"
  }
}
```

### Update Order Status

Update order status. **Requires admin authentication.**

```http
PATCH /api/orders/{order_id}
```

**Request Body:**
```json
{
  "status": "confirmed"
}
```

**Valid statuses:**
- `unconfirmed` - Order placed, awaiting confirmation
- `confirmed` - Order confirmed by admin
- `in progress` - Order being processed
- `completed` - Order fulfilled
- `cancelled` - Order cancelled

**Example:**
```bash
curl -X PATCH http://localhost:5000/api/orders/ORD000001 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "status": "confirmed"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Order status updated successfully"
}
```

### Lookup Order

Find order by email and order ID (for customer tracking).

```http
GET /api/orders/lookup?email={email}&order_id={order_id}
```

**Example:**
```bash
curl "http://localhost:5000/api/orders/lookup?email=john@example.com&order_id=ORD000001"
```

**Response:** Same as Get Order endpoint

---

## Health Check

Check if the API is running.

```http
GET /api/health
```

**Example:**
```bash
curl http://localhost:5000/api/health
```

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "service": "laptop-inventory-admin-api",
  "version": "2.0.0"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Missing required field: brand"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Unauthorized - API key required"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Laptop not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Database connection error"
}
```

---

## API Testing

### Using cURL

```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Get all laptops
curl http://localhost:5000/api/laptops

# Get specific laptop
curl http://localhost:5000/api/laptops/507f1f77bcf86cd799439011

# Create laptop (with admin key)
curl -X POST http://localhost:5000/api/laptops \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"brand":"Dell","model":"XPS 13","selling_price":1500}'
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:5000/api"
API_KEY = "your-api-key"

# Get all laptops
response = requests.get(f"{BASE_URL}/laptops")
laptops = response.json()

# Create a laptop
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}
data = {
    "brand": "Dell",
    "model": "XPS 13",
    "cpu": "Intel i7",
    "ram": "16GB",
    "storage": "512GB SSD",
    "selling_price": 1500.00
}
response = requests.post(f"{BASE_URL}/laptops", json=data, headers=headers)
print(response.json())
```

### Using Postman

1. Import collection from the examples above
2. Set base URL variable: `http://localhost:5000/api`
3. Set API key in headers: `X-API-Key: your-key`
4. Test each endpoint

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider:
- 100 requests per minute per IP
- Higher limits for authenticated users
- Use Flask-Limiter extension

## CORS

CORS is enabled for all origins in development. For production:
- Configure specific allowed origins
- Set appropriate headers
- Use credentials mode for cookies

## Versioning

Current version: **v2.0.0**

API versioning via URL path:
- Current: `/api/*` (v2)
- Future: `/api/v3/*` (when breaking changes needed)

---

## Quick Reference

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/laptops` | No | List all laptops |
| GET | `/api/laptops/{id}` | No | Get laptop details |
| POST | `/api/laptops` | Yes | Create laptop |
| PUT | `/api/laptops/{id}` | Yes | Full update laptop |
| PATCH | `/api/laptops/{id}` | Yes | Partial update laptop |
| DELETE | `/api/laptops/{id}` | Yes | Delete laptop |
| GET | `/api/spare-parts` | No | List spare parts |
| GET | `/api/spare-parts/{id}` | No | Get spare part |
| POST | `/api/spare-parts` | Yes | Create spare part |
| PUT | `/api/spare-parts/{id}` | Yes | Update spare part |
| DELETE | `/api/spare-parts/{id}` | Yes | Delete spare part |
| POST | `/api/orders` | No | Create order |
| GET | `/api/orders/{id}` | No | Get order |
| PATCH | `/api/orders/{id}` | Yes | Update order status |
| GET | `/api/orders/lookup` | No | Lookup order |
| GET | `/api/health` | No | Health check |

---

## Next Steps

- Implement API key management
- Add rate limiting
- Add pagination for list endpoints
- Add sorting and advanced filtering
- Implement webhook notifications
- Add bulk operations
- Create OpenAPI/Swagger documentation
