# Deployment Guide

Different ways to deploy this application depending on your needs.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Manual Installation](#manual-installation)
3. [MongoDB Atlas (Cloud)](#mongodb-atlas-cloud)
4. [VPS Deployment](#vps-deployment)
5. [Raspberry Pi](#raspberry-pi)
6. [Production Setup](#production-setup)

---

## Docker Deployment

Easiest method using Docker Compose.

**Prerequisites:** Docker 20.10+, Docker Compose v2.0+

### Steps

1. Clone and configure
   ```bash
   git clone https://github.com/Ang-edgar/mongodb-laptop-inventory-manager.git
   cd mongodb-laptop-inventory-manager
   cp .env.example .env
   # Edit .env with your settings
   ```

2. Start containers
   ```bash
   docker-compose up -d
   ```

3. Initialize database
   ```bash
   docker-compose exec web python scripts/init_db.py
   ```

4. Access at http://localhost:5000
   - Default login: admin/admin123

### Useful Commands

```bash
# View logs
docker-compose logs -f web

# Restart
docker-compose restart

# Stop everything
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

---

## Manual Installation

For development or if you don't want to use Docker.

**Prerequisites:** Python 3.10+, MongoDB 5.0+

### Install MongoDB

Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y mongodb
sudo systemctl start mongodb
```

macOS:
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

Windows: Download from [mongodb.com](https://www.mongodb.com/try/download/community)

### Setup Application

```bash
git clone https://github.com/Ang-edgar/mongodb-laptop-inventory-manager.git
cd mongodb-laptop-inventory-manager

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env

# Initialize database
python scripts/init_db.py

# Run
cd app
python __init__.py
```

Access at http://localhost:5000

---

## MongoDB Atlas (Cloud)

Use MongoDB's free cloud database (512MB free tier).

### Setup

1. Create account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)

2. Create free cluster (M0 tier)
   - Click "Build a Database"
   - Choose FREE tier
   - Select nearest region

3. Setup database user
   - Go to "Database Access"
   - Add user with password auth
   - Grant "Read and write to any database"

4. Whitelist IP addresses
   - Go to "Network Access"
   - Add `0.0.0.0/0` for testing (allows all IPs)
   - For production: add specific IPs only

5. Get connection string
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your actual password

6. Update your `.env`:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/laptop_inventory?retryWrites=true&w=majority
   ```

7. Run init script:
   ```bash
   python scripts/init_db.py
   ```

---

## VPS Deployment

Deploy on any VPS provider (DigitalOcean, Linode, AWS EC2, etc.).

**Requirements:** Ubuntu 22.04+ server with 2GB RAM minimum

### Initial Setup

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose-plugin -y
```

### Deploy Application

```bash
# Clone app
cd /opt
git clone https://github.com/Ang-edgar/mongodb-laptop-inventory-manager.git
cd mongodb-laptop-inventory-manager

# Configure
cp .env.example .env
nano .env
# Set FLASK_ENV=production, change passwords, etc.

# Start
docker-compose up -d
```

### Setup Nginx (Optional)

For better performance and HTTPS support:

```bash
apt install nginx -y
nano /etc/nginx/sites-available/laptop-inventory
```

Add this config:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:
```bash
ln -s /etc/nginx/sites-available/laptop-inventory /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Add SSL with Let's Encrypt

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

Certbot will auto-configure HTTPS.

---

## Raspberry Pi

Works on Raspberry Pi 4 with 4GB+ RAM.

### Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in

# Install Docker Compose
sudo apt install docker-compose -y

# Clone app
cd ~
git clone https://github.com/Ang-edgar/mongodb-laptop-inventory-manager.git
cd mongodb-laptop-inventory-manager

# Configure
cp .env.example .env
nano .env

# Start
docker-compose up -d
```

### Auto-start on Boot

```bash
crontab -e
```

Add:
```
@reboot cd /home/pi/mongodb-laptop-inventory-manager && docker-compose up -d
```

Access on local network: `http://raspberry-pi-ip:5000`

---

## Production Setup

### Security Checklist

1. **Change default credentials**
   ```env
   ADMIN_PASSWORD=strong-unique-password
   SECRET_KEY=generate-with-openssl-rand-hex-32
   ```

2. **Enable MongoDB authentication**
   
   In `docker-compose.yml`:
   ```yaml
   mongodb:
     environment:
       MONGO_INITDB_ROOT_USERNAME: admin
       MONGO_INITDB_ROOT_PASSWORD: strong-password
   ```
   
   Update connection in `.env`:
   ```env
   MONGODB_URI=mongodb://admin:strong-password@mongodb:27017/laptop_inventory?authSource=admin
   ```

3. **Use HTTPS** (see Nginx + Let's Encrypt above)

4. **Configure firewall**
   ```bash
   ufw allow 22/tcp    # SSH
   ufw allow 80/tcp    # HTTP
   ufw allow 443/tcp   # HTTPS
   ufw enable
   ```

### Backups

Create a backup script (`backup.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
docker-compose exec -T mongodb mongodump \
  --archive=$BACKUP_DIR/backup_$DATE.archive \
  --gzip

# Keep last 7 days only
find $BACKUP_DIR -name "backup_*.archive" -mtime +7 -delete
```

Make executable and add to cron:
```bash
chmod +x backup.sh
crontab -e
```

Add daily backup at 2 AM:
```
0 2 * * * /opt/mongodb-laptop-inventory-manager/backup.sh
```

### Monitoring

Check if everything's running:
```bash
docker-compose ps
docker-compose logs -f --tail=100
```

MongoDB stats:
```bash
docker-compose exec mongodb mongosh --eval "db.stats()"
```

---

## Troubleshooting

**MongoDB won't connect:**
```bash
docker-compose ps
docker-compose logs mongodb
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

**Application errors:**
```bash
docker-compose logs web
docker-compose restart web
```

**Port conflicts:**
```bash
sudo lsof -i :5000
# Kill process or change PORT in .env
```

**Out of memory (Raspberry Pi):**
- Reduce Docker memory limits in docker-compose.yml
- Use external MongoDB Atlas instead

---

That's it. Choose the deployment method that fits your needs.

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
