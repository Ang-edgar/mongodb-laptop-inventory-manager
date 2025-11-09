# Changelog

## [2.0.0] - 2025-11-09

### Major Release: Microservices Architecture + JWT Authentication

This release represents a complete architectural transformation from a monolithic application to a modern, cloud-native microservices system with enterprise-grade authentication.

### 🎯 New Features

#### Authentication System
- **JWT Authentication**: Stateless token-based authentication system
- **User Registration**: Email-based account creation with validation
- **User Login**: Secure authentication with bcrypt password hashing
- **Session Management**: HttpOnly cookies for XSS protection
- **Token Expiration**: Automatic 24-hour token expiration
- **Protected Routes**: `@login_required` decorator for secure endpoints
- **User Profiles**: Name, email, and account management

#### Microservices Architecture
- **Admin Backend**: Centralized API server (Port 5000)
- **Guest Frontend**: Customer-facing application (Port 5001)
- **REST API**: 8 API endpoints with CORS support
- **Independent Deployment**: Deploy admin and guest separately
- **Multi-Region Support**: Deploy guest apps in multiple locations

#### Kubernetes Ready
- **Stateless Design**: No session affinity required
- **Horizontal Scaling**: Deploy unlimited replicas
- **Cloud-Native**: Works with any Kubernetes platform
- **Auto-scaling**: HPA manifests included
- **Load Balancing**: Works with any load balancer

### 🔧 Technical Improvements

#### Security
- **bcrypt Hashing**: Cost factor 12 for password security
- **JWT Signing**: HS256 algorithm with secret key
- **HttpOnly Cookies**: Protection against XSS attacks
- **SameSite Cookies**: CSRF protection
- **Unique Email Index**: Prevent duplicate accounts
- **Password Validation**: Minimum length requirements

#### Database
- **New Users Collection**: MongoDB collection for authentication
- **Email Index**: Unique index for fast lookups
- **User Linking**: Orders linked to user accounts
- **Schema Updates**: User ID in orders collection

#### API & Integration
- **8 REST Endpoints**: Complete API for guest apps
- **CORS Support**: Cross-origin requests enabled
- **Health Checks**: `/api/health` endpoint
- **Error Handling**: Proper HTTP status codes
- **JSON Responses**: Consistent API response format

#### Docker & Deployment
- **docker-compose-microservices.yml**: New compose file
- **Guest Dockerfile**: Separate guest app container
- **Environment Variables**: Proper configuration management
- **Volume Mounts**: Development-friendly setup
- **Network Configuration**: Service discovery

### 📚 Documentation

#### New Documentation
- **docs/AUTHENTICATION.md**: Complete JWT authentication guide
  - Architecture overview
  - Security best practices
  - Kubernetes deployment
  - Troubleshooting guide
  
- **MICROSERVICES.md**: Microservices architecture guide
  - System architecture diagrams
  - API endpoint documentation
  - Deployment strategies
  - Scaling patterns
  
- **guest-app/README.md**: Guest application documentation
  - Setup instructions
  - Configuration guide
  - Deployment options
  - Kubernetes manifests

#### Updated Documentation
- **README.md**: Complete rewrite with:
  - Microservices overview
  - Authentication features
  - Updated installation steps
  - API documentation
  - Kubernetes deployment info
  
- **DEPLOYMENT.md**: Enhanced with:
  - Microservices deployment
  - JWT configuration
  - Security checklist
  - Multi-region setup

### 🏗️ Architecture Changes

#### Before (v1.x - Monolithic)
```
Web App (Port 5000)
└── MongoDB (Port 27017)
```

#### After (v2.0 - Microservices)
```
Guest Apps (Ports 5001+)  ──┐
Guest Apps (Multiple)      ├──► Admin API (Port 5000) ──► MongoDB (Port 27017)
Guest Apps (Multi-Region)  ──┘
```

### 📦 Dependencies

#### New Dependencies
- **PyJWT 2.8.0**: JWT token generation and validation
- **bcrypt 4.1.2**: Secure password hashing
- **flask-cors 4.0.0**: Cross-Origin Resource Sharing
- **pymongo 4.6.0**: MongoDB driver (guest app)

#### Updated Dependencies
- Flask 2.3.3 (maintained)
- PyMongo 4.6.0 (maintained)
- Bootstrap 5.1.3 (maintained)

### 🚀 Migration Guide

#### From v1.x to v2.0

**Option 1: Keep Monolithic (No Changes Needed)**
```bash
docker-compose up -d
# Continue using port 5000
```

**Option 2: Migrate to Microservices**
```bash
# Stop old containers
docker-compose down

# Start microservices
docker-compose -f docker-compose-microservices.yml up -d

# Access new endpoints:
# - Guest: http://localhost:5001
# - Admin: http://localhost:5000/admin
# - API: http://localhost:5000/api
```

**Database Migration**
No database changes required! The new users collection is automatically created on first user registration. All existing laptops, orders, and spare parts work as-is.

### 🔒 Security Updates

1. **Password Storage**: Moved from plain text to bcrypt hashing
2. **Authentication**: Session-based → JWT token-based
3. **Cookie Security**: Added HttpOnly and SameSite flags
4. **API Security**: Added CORS configuration
5. **Secret Management**: Environment variable based

### ⚡ Performance Improvements

1. **Stateless Auth**: No server-side session storage
2. **Independent Scaling**: Scale guest apps independently
3. **Edge Deployment**: Deploy guest apps near users
4. **API Caching**: Cacheable API responses
5. **MongoDB Indexes**: Optimized user lookups

### 🐛 Bug Fixes

- Fixed date handling in templates (strftime → string slicing)
- Fixed cart add functionality (complete data passing)
- Fixed cart remove functionality (index-based removal)
- Fixed checkout template (stored cart data usage)
- Fixed API imports (correct module paths)
- Fixed API method names (find_by_id vs get_by_id)

### 📋 Breaking Changes

#### Configuration
- **New Environment Variables Required**:
  - `JWT_SECRET`: Required for guest app authentication
  - `ADMIN_API_URL`: Required for guest app
  - `JWT_EXPIRATION_HOURS`: Optional (default 24)

#### Deployment
- **New Docker Compose File**: Use `docker-compose-microservices.yml`
- **Port Changes**: Guest app now on 5001 (admin stays on 5000)
- **Network Changes**: Services communicate via Docker network

#### API
- **CORS Enabled**: All API endpoints support cross-origin
- **New Routes**: `/register`, `/login`, `/logout` on guest app
- **Auth Required**: Some routes may require authentication

### 🎓 Learning Resources

- [Microservices Architecture](MICROSERVICES.md)
- [JWT Authentication Deep Dive](docs/AUTHENTICATION.md)
- [Kubernetes Deployment Guide](docs/AUTHENTICATION.md#kubernetes-deployment)
- [Security Best Practices](docs/AUTHENTICATION.md#security-best-practices)

### 🙏 Credits

Developed by Edgar Effendi
- Architecture redesign
- JWT authentication implementation
- Microservices separation
- Kubernetes optimization
- Documentation overhaul

### 📈 Statistics

- **Files Added**: 21 new files
- **Files Modified**: 6 files
- **Lines of Code**: +3,842 additions, -103 deletions
- **Documentation**: 4 comprehensive guides
- **API Endpoints**: 8 REST endpoints
- **Docker Services**: 3 microservices

### 🔮 Future Roadmap

- [ ] Email verification for registration
- [ ] Password reset functionality
- [ ] OAuth integration (Google, Facebook)
- [ ] Refresh tokens for extended sessions
- [ ] User profiles and preferences
- [ ] Role-based access control (RBAC)
- [ ] Order history in user dashboard
- [ ] Real-time notifications
- [ ] GraphQL API option
- [ ] Monitoring and observability

### 📞 Support

- **Issues**: https://github.com/Ang-edgar/mongodb-laptop-inventory-manager/issues
- **Email**: edgarwineffendi@gmail.com
- **Documentation**: See README.md and docs/

---

## [1.0.0] - 2025-11-08

### Initial Release

- Basic laptop inventory management
- Admin panel
- Guest shopping interface
- MongoDB integration
- Docker deployment
- Session-based cart
