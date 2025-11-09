# JWT Authentication System

## Overview
Stateless JWT-based authentication system designed for Kubernetes scalability.

## Architecture

### Technology Stack
- **JWT**: JSON Web Tokens for stateless authentication
- **bcrypt**: Secure password hashing
- **MongoDB**: User account storage
- **Cookies**: Token storage in browser (httponly, secure)

### Why JWT for Kubernetes?
- **Stateless**: No session storage needed
- **Scalable**: Works across multiple pods without session affinity
- **Simple**: No Redis/Memcached dependency
- **Secure**: Tokens are signed and expire automatically

## Features

### User Management
- Registration with email/password
- Login with JWT token generation
- Secure password hashing with bcrypt
- Token expiration (24 hours default)

### Security Features
- HttpOnly cookies (prevents XSS attacks)
- Password minimum length (6 characters)
- Unique email constraint
- Token signing with secret key
- Automatic token expiration

## API Endpoints

### Authentication Routes
- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - User logout (clears token)

### Protected Routes (Future)
You can protect any route with the `@login_required` decorator:

```python
from auth import login_required

@app.route('/protected')
@login_required
def protected_route():
    user = request.current_user
    return f"Hello {user['name']}"
```

## Database Schema

### Users Collection
```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "password": "bcrypt_hash",
  "name": "John Doe",
  "created_at": ISODate,
  "is_active": true
}
```

### Indexes
- `email`: Unique index for fast lookups and uniqueness constraint

## JWT Token Payload
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "exp": 1699574400,
  "iat": 1699488000
}
```

## Configuration

### Environment Variables
```env
# Required
JWT_SECRET=your-secret-key-change-in-production
MONGODB_URI=mongodb://mongodb:27017/

# Optional
JWT_EXPIRATION_HOURS=24
SECRET_KEY=flask-secret-key
```

## Kubernetes Deployment

### No Special Configuration Needed!
The stateless JWT design means:
- ✅ No session storage required
- ✅ No sticky sessions needed
- ✅ Works with any number of replicas
- ✅ Horizontal Pod Autoscaling ready

### Example Kubernetes Deployment
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
        env:
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: auth-secrets
              key: jwt-secret
        - name: MONGODB_URI
          value: "mongodb://mongodb-service:27017/"
```

### Autoscaling
```yaml
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

## Usage

### 1. Register a New User
Navigate to `/register` and create an account.

### 2. Login
Navigate to `/login` with your credentials.

### 3. Token Storage
- Token is stored in an httpOnly cookie
- Automatically included in all requests
- No JavaScript access (XSS protection)

### 4. Access Protected Features
- Cart persists across sessions
- Order history tied to user account
- Personalized experience

## Future Enhancements

### Optional Improvements
1. **Email Verification**: Send verification emails
2. **Password Reset**: Forgot password flow
3. **OAuth Integration**: Google/Facebook login
4. **Refresh Tokens**: Long-term authentication
5. **User Profiles**: Address book, preferences
6. **Role-Based Access**: Admin, customer, guest roles

## Security Best Practices

### Production Checklist
- [ ] Change `JWT_SECRET` to a strong random value
- [ ] Use HTTPS in production
- [ ] Set secure cookie flag when using HTTPS
- [ ] Implement rate limiting on login endpoints
- [ ] Add CAPTCHA to prevent brute force
- [ ] Monitor failed login attempts
- [ ] Regular security audits

## Testing

### Test User Registration
```bash
curl -X POST http://localhost:5001/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=John Doe&email=john@example.com&password=password123&confirm_password=password123"
```

### Test Login
```bash
curl -X POST http://localhost:5001/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=john@example.com&password=password123" \
  -c cookies.txt
```

### Access Protected Resource
```bash
curl http://localhost:5001/cart \
  -b cookies.txt
```

## Troubleshooting

### Common Issues

1. **"Authentication required" error**
   - Check if token is in cookie
   - Verify token hasn't expired
   - Ensure JWT_SECRET matches

2. **"Email already registered"**
   - Email must be unique
   - Use different email or login

3. **MongoDB connection error**
   - Verify MONGODB_URI is correct
   - Check MongoDB is running
   - Check network connectivity

## Monitoring

### Key Metrics to Track
- Registration rate
- Login success/failure rate
- Token expiration events
- Active users
- Authentication latency

### Logging
All authentication events are logged with:
- Timestamp
- User email
- Action (register/login/logout)
- Success/failure
- IP address (if needed)

## Conclusion

This authentication system is:
- ✅ **Kubernetes-ready**: Stateless and scalable
- ✅ **Secure**: Industry-standard JWT + bcrypt
- ✅ **Simple**: Minimal dependencies
- ✅ **Production-ready**: With proper configuration
- ✅ **Future-proof**: Easy to extend with new features
