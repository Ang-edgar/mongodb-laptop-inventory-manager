# Deployment Guide

This guide covers various deployment scenarios for the MongoDB Laptop Inventory Management System.

## Table of Contents

1. [Docker Deployment (Recommended)](#docker-deployment-recommended)
2. [Manual Installation](#manual-installation)
3. [MongoDB Atlas (Cloud)](#mongodb-atlas-cloud)
4. [Self-Hosted on VPS](#self-hosted-on-vps)
5. [Raspberry Pi Deployment](#raspberry-pi-deployment)
6. [Production Considerations](#production-considerations)

---

## Docker Deployment (Recommended)

The easiest way to deploy is using Docker Compose.

### Prerequisites
- Docker (20.10+)
- Docker Compose (v2.0+)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/laptop-inventory-management.git
   cd laptop-inventory-management
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   nano .env
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize database**
   ```bash
   docker-compose exec web python scripts/init_db.py
   ```

5. **Access application**
   - URL: http://localhost:5000
   - Admin: `admin` / `admin123`

### Docker Commands

```bash
# View logs
docker-compose logs -f web

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

---

## Manual Installation

For development or non-containerized deployments.

### Prerequisites
- Python 3.10+
- MongoDB 5.0+

### Steps

1. **Install MongoDB**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y mongodb
   sudo systemctl start mongodb
   sudo systemctl enable mongodb
   ```
   
   **macOS:**
   ```bash
   brew tap mongodb/brew
   brew install mongodb-community
   brew services start mongodb-community
   ```
   
   **Windows:**
   - Download from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - Run installer and follow wizard

2. **Clone and setup application**
   ```bash
   git clone https://github.com/yourusername/laptop-inventory-management.git
   cd laptop-inventory-management
   ```

3. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env
   ```

6. **Initialize database**
   ```bash
   python scripts/init_db.py
   ```

7. **Run application**
   ```bash
   cd app
   python __init__.py
   ```

8. **Access application**
   - URL: http://localhost:5000

---

## MongoDB Atlas (Cloud)

Deploy with MongoDB's cloud database service.

### Steps

1. **Create MongoDB Atlas Account**
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up for free tier (512MB storage)

2. **Create Cluster**
   - Click "Build a Database"
   - Choose FREE tier (M0)
   - Select region closest to users
   - Click "Create Cluster"

3. **Configure Database Access**
   - Go to "Database Access"
   - Add new database user
   - Choose password authentication
   - Set username and strong password
   - Grant "Read and write to any database" role

4. **Configure Network Access**
   - Go to "Network Access"
   - Add IP address
   - For testing: Add `0.0.0.0/0` (allows all)
   - For production: Add specific IPs

5. **Get Connection String**
   - Go to "Database" → "Connect"
   - Choose "Connect your application"
   - Copy connection string
   - Replace `<password>` with your password

6. **Update Application**
   ```bash
   # .env file
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/laptop_inventory?retryWrites=true&w=majority
   ```

7. **Initialize database**
   ```bash
   python scripts/init_db.py
   ```

---

## Self-Hosted on VPS

Deploy on a Virtual Private Server (e.g., DigitalOcean, Linode, AWS EC2).

### Prerequisites
- VPS with Ubuntu 22.04+ (2GB RAM minimum)
- Domain name (optional but recommended)

### Steps

1. **Connect to VPS**
   ```bash
   ssh root@your-server-ip
   ```

2. **Update system**
   ```bash
   apt update && apt upgrade -y
   ```

3. **Install Docker and Docker Compose**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Install Docker Compose
   apt install docker-compose-plugin -y
   ```

4. **Clone application**
   ```bash
   cd /opt
   git clone https://github.com/yourusername/laptop-inventory-management.git
   cd laptop-inventory-management
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env
   ```
   
   Update:
   ```env
   SECRET_KEY=generate-a-strong-random-key-here
   FLASK_ENV=production
   ADMIN_PASSWORD=strong-unique-password
   ```

6. **Start services**
   ```bash
   docker-compose up -d
   ```

7. **Setup Nginx reverse proxy (optional)**
   ```bash
   apt install nginx -y
   nano /etc/nginx/sites-available/laptop-inventory
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```
   
   Enable site:
   ```bash
   ln -s /etc/nginx/sites-available/laptop-inventory /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

8. **Setup SSL with Let's Encrypt (recommended)**
   ```bash
   apt install certbot python3-certbot-nginx -y
   certbot --nginx -d your-domain.com
   ```

---

## Raspberry Pi Deployment

Deploy on Raspberry Pi for home/small business use.

### Prerequisites
- Raspberry Pi 4 (4GB+ RAM recommended)
- Raspberry Pi OS (64-bit)
- Static IP or DDNS setup

### Steps

1. **Update system**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```
   
   Log out and back in for group changes to take effect.

3. **Install Docker Compose**
   ```bash
   sudo apt install docker-compose -y
   ```

4. **Clone application**
   ```bash
   cd ~
   git clone https://github.com/yourusername/laptop-inventory-management.git
   cd laptop-inventory-management
   ```

5. **Configure for Raspberry Pi**
   ```bash
   cp .env.example .env
   nano .env
   ```

6. **Update docker-compose.yml for ARM architecture**
   - The MongoDB image should support ARM64
   - Or use MongoDB from apt:
   ```bash
   sudo apt install mongodb -y
   ```
   
   Then update `.env`:
   ```env
   MONGODB_URI=mongodb://localhost:27017/laptop_inventory
   ```

7. **Start application**
   ```bash
   docker-compose up -d
   ```

8. **Setup autostart**
   ```bash
   # Add to crontab
   crontab -e
   ```
   
   Add line:
   ```
   @reboot cd /home/pi/laptop-inventory-management && docker-compose up -d
   ```

9. **Access locally**
   - URL: http://raspberry-pi-ip:5000

---

## Production Considerations

### Security

1. **Change Default Credentials**
   ```bash
   # Update .env
   ADMIN_PASSWORD=strong-unique-password-here
   SECRET_KEY=generate-random-secret-key
   ```

2. **Enable MongoDB Authentication**
   ```yaml
   # docker-compose.yml
   mongodb:
     environment:
       MONGO_INITDB_ROOT_USERNAME: admin
       MONGO_INITDB_ROOT_PASSWORD: strong-password
   ```
   
   Update connection string:
   ```env
   MONGODB_URI=mongodb://admin:strong-password@mongodb:27017/laptop_inventory?authSource=admin
   ```

3. **Use HTTPS**
   - Setup SSL certificate (Let's Encrypt)
   - Use reverse proxy (Nginx/Caddy)

4. **Firewall Configuration**
   ```bash
   # Ubuntu UFW
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 80/tcp    # HTTP
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw enable
   ```

### Backup

1. **MongoDB Backup Script**
   ```bash
   #!/bin/bash
   # backup.sh
   BACKUP_DIR="/backups/mongodb"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   mkdir -p $BACKUP_DIR
   docker-compose exec -T mongodb mongodump \
     --archive=$BACKUP_DIR/backup_$DATE.archive \
     --gzip
   
   # Keep only last 7 days
   find $BACKUP_DIR -name "backup_*.archive" -mtime +7 -delete
   ```

2. **Setup daily backups**
   ```bash
   chmod +x backup.sh
   
   # Add to crontab
   crontab -e
   ```
   
   Add:
   ```
   0 2 * * * /path/to/backup.sh
   ```

### Monitoring

1. **Check application health**
   ```bash
   curl http://localhost:5000
   ```

2. **Monitor logs**
   ```bash
   docker-compose logs -f --tail=100
   ```

3. **MongoDB stats**
   ```bash
   docker-compose exec mongodb mongosh --eval "db.stats()"
   ```

### Performance

1. **Enable MongoDB Indexes** (already configured in init_db.py)

2. **Optimize Docker resources**
   ```yaml
   # docker-compose.yml
   services:
     web:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 512M
   ```

3. **Use production WSGI server**
   ```bash
   pip install gunicorn
   
   # Run with:
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

---

## Troubleshooting

### MongoDB Connection Issues
```bash
# Check MongoDB is running
docker-compose ps

# Check MongoDB logs
docker-compose logs mongodb

# Test connection
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

### Application Errors
```bash
# View application logs
docker-compose logs web

# Restart application
docker-compose restart web
```

### Port Already in Use
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>
```

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/laptop-inventory-management/issues
- Documentation: See README.md

---

**Built with ❤️ using Flask and MongoDB**
