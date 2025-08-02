# Deployment Guide - Train Ticket Booking System

## Table of Contents
- [System Requirements](#system-requirements)
- [Local Development Setup](#local-development-setup)
- [Database Setup](#database-setup)
- [Environment Configuration](#environment-configuration)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## System Requirements

### Minimum Requirements
- **Python**: 3.7 or higher
- **MySQL**: 5.7 or higher (or MariaDB 10.2+)
- **RAM**: 512MB minimum, 1GB recommended
- **Storage**: 100MB for application, additional space for database
- **OS**: Linux, Windows, macOS

### Recommended Requirements
- **Python**: 3.9+
- **MySQL**: 8.0+
- **RAM**: 2GB+
- **Storage**: 1GB+ with SSD
- **OS**: Ubuntu 20.04 LTS or CentOS 8

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Mahanth6666/TRAIN_TICKET_BOOKING_ADVANCED.git
cd TRAIN_TICKET_BOOKING_ADVANCED
```

### 2. Create Virtual Environment

#### On Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

#### Create `requirements.txt`:
```text
Flask==2.3.3
mysql-connector-python==8.2.0
python-dotenv==1.0.0
```

#### Install packages:
```bash
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import flask, mysql.connector; print('Dependencies installed successfully')"
```

## Database Setup

### 1. Install MySQL

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install mysql-server mysql-client
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### CentOS/RHEL:
```bash
sudo yum install mysql-server mysql
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

#### Windows:
Download and install MySQL from [https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/)

#### macOS:
```bash
brew install mysql
brew services start mysql
```

### 2. Secure MySQL Installation

```bash
sudo mysql_secure_installation
```

Follow the prompts to:
- Set root password
- Remove anonymous users
- Disable root remote login
- Remove test database

### 3. Create Database and User

#### Connect to MySQL:
```bash
mysql -u root -p
```

#### Execute SQL commands:
```sql
-- Create database
CREATE DATABASE train CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (replace 'your_password' with a strong password)
CREATE USER 'train_user'@'localhost' IDENTIFIED BY 'your_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON train.* TO 'train_user'@'localhost';
FLUSH PRIVILEGES;

-- Use the database
USE train;
```

### 4. Create Tables

#### Execute the following SQL schema:

```sql
-- Users table
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    role ENUM('customer', 'manager') NOT NULL DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Class coach table
CREATE TABLE class_coach (
    sno INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    base_cost DECIMAL(10,2) NOT NULL,
    description TEXT
);

-- Destinations table
CREATE TABLE desti (
    dno INT AUTO_INCREMENT PRIMARY KEY,
    destination VARCHAR(100) NOT NULL UNIQUE,
    cost DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trains table
CREATE TABLE traind (
    tid INT AUTO_INCREMENT PRIMARY KEY,
    train_name VARCHAR(100) NOT NULL,
    destination1 VARCHAR(100) NOT NULL,
    destination2 VARCHAR(100) NOT NULL,
    destination3 VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Passengers table
CREATE TABLE passenger (
    pno INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL CHECK (age > 0 AND age < 150),
    phonenum BIGINT NOT NULL,
    reg_date DATE NOT NULL,
    startingpoint VARCHAR(100) NOT NULL DEFAULT 'Coimbatore',
    totalcost DECIMAL(10,2) NOT NULL,
    tickets INT NOT NULL CHECK (tickets > 0),
    tid INT NOT NULL,
    destination VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tid (tid),
    INDEX idx_destination (destination),
    INDEX idx_reg_date (reg_date)
);
```

### 5. Insert Sample Data

```sql
-- Sample class coaches
INSERT INTO class_coach (class_name, base_cost, description) VALUES
('Second Seater', 2000.00, 'Economy class with basic seating'),
('Sleeper Class', 4000.00, 'Comfortable sleeper berths'),
('First Class AC', 6000.00, 'Premium air-conditioned compartment');

-- Sample destinations
INSERT INTO desti (destination, cost) VALUES
('Chennai', 500.00),
('Bangalore', 300.00),
('Mumbai', 1200.00),
('Delhi', 2000.00),
('Kolkata', 1500.00);

-- Sample trains
INSERT INTO traind (train_name, destination1, destination2, destination3) VALUES
('Shatabdi Express', 'Chennai', 'Bangalore', 'Mumbai'),
('Rajdhani Express', 'Delhi', 'Mumbai', 'Kolkata'),
('Duronto Express', 'Chennai', 'Delhi', 'Bangalore');

-- Sample admin user (password: admin123)
INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'manager');

-- Sample customer user (password: user123)
INSERT INTO users (username, password, role) VALUES
('customer1', 'user123', 'customer');
```

## Environment Configuration

### 1. Create Environment File

Create `.env` file in the project root:

```bash
# Database Configuration
DB_HOST=localhost
DB_USER=train_user
DB_PASSWORD=your_password
DB_NAME=train
DB_PORT=3306

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Application Settings
DEFAULT_STARTING_POINT=Coimbatore
```

### 2. Update `app.py` for Environment Variables

Add at the top of `app.py`:

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))

def get_db_connection():
    try:
        con = mysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'train'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        if con.is_connected():
            print("Connected to the database")
        return con
    except mysql.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
```

### 3. Create Configuration Class

Create `config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-secret-key'
    
    # Database settings
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'train')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Application settings
    DEFAULT_STARTING_POINT = os.getenv('DEFAULT_STARTING_POINT', 'Coimbatore')

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
class TestingConfig(Config):
    TESTING = True
    DB_NAME = 'train_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

## Local Testing

### 1. Run the Application

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Run the application
python app.py
```

### 2. Access the Application

Open your browser and navigate to:
- **Local URL**: `http://127.0.0.1:5000`
- **Network URL**: `http://localhost:5000`

### 3. Test Basic Functionality

1. **Register a new user**:
   - Go to `/register`
   - Create accounts with both 'customer' and 'manager' roles

2. **Login and test features**:
   - Customer: Book tickets, view trains
   - Manager: Manage passengers, trains, destinations

3. **Verify database operations**:
   ```bash
   mysql -u train_user -p train
   SELECT * FROM users;
   SELECT * FROM passenger;
   ```

## Production Deployment

### 1. Server Setup (Ubuntu 20.04)

#### Update system:
```bash
sudo apt update && sudo apt upgrade -y
```

#### Install required packages:
```bash
sudo apt install python3 python3-pip python3-venv nginx mysql-server git -y
```

#### Create application user:
```bash
sudo adduser trainapp
sudo usermod -aG sudo trainapp
sudo su - trainapp
```

### 2. Application Deployment

#### Clone and setup:
```bash
cd /home/trainapp
git clone https://github.com/Mahanth6666/TRAIN_TICKET_BOOKING_ADVANCED.git app
cd app

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Create production environment file:
```bash
cat > .env << EOF
DB_HOST=localhost
DB_USER=train_user
DB_PASSWORD=STRONG_PRODUCTION_PASSWORD
DB_NAME=train
DB_PORT=3306
FLASK_ENV=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DEFAULT_STARTING_POINT=Coimbatore
EOF
```

### 3. Configure Gunicorn

#### Install Gunicorn:
```bash
pip install gunicorn
```

#### Create Gunicorn configuration:
```bash
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 2
user = "trainapp"
group = "trainapp"
timeout = 120
keepalive = 5
max_requests = 1000
preload_app = True
capture_output = True
enable_stdio_inheritance = True
EOF
```

#### Test Gunicorn:
```bash
gunicorn --config gunicorn.conf.py app:app
```

### 4. Configure Systemd Service

#### Create service file:
```bash
sudo tee /etc/systemd/system/trainapp.service << EOF
[Unit]
Description=Train Ticket Booking Application
After=network.target

[Service]
User=trainapp
Group=trainapp
WorkingDirectory=/home/trainapp/app
Environment=PATH=/home/trainapp/app/venv/bin
ExecStart=/home/trainapp/app/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

#### Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable trainapp
sudo systemctl start trainapp
sudo systemctl status trainapp
```

### 5. Configure Nginx

#### Create Nginx configuration:
```bash
sudo tee /etc/nginx/sites-available/trainapp << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    location /static {
        alias /home/trainapp/app/static;
        expires 30d;
    }
    
    client_max_body_size 10M;
}
EOF
```

#### Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/trainapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Configuration (Let's Encrypt)

#### Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx -y
```

#### Obtain SSL certificate:
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

#### Test auto-renewal:
```bash
sudo certbot renew --dry-run
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' trainapp
RUN chown -R trainapp:trainapp /app
USER trainapp

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000')" || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
```

### 2. Create Docker Compose

```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    container_name: trainapp_db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: train
      MYSQL_USER: train_user
      MYSQL_PASSWORD: userpassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - trainapp_network

  web:
    build: .
    container_name: trainapp_web
    restart: always
    environment:
      DB_HOST: db
      DB_USER: train_user
      DB_PASSWORD: userpassword
      DB_NAME: train
      DB_PORT: 3306
      FLASK_ENV: production
      SECRET_KEY: your-secret-key-here
    ports:
      - "5000:5000"
    depends_on:
      - db
    networks:
      - trainapp_network
    volumes:
      - ./logs:/app/logs

  nginx:
    image: nginx:alpine
    container_name: trainapp_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    networks:
      - trainapp_network

volumes:
  mysql_data:

networks:
  trainapp_network:
    driver: bridge
```

### 3. Create Database Initialization Script

Create `init.sql` with the database schema from the Database Setup section.

### 4. Deploy with Docker

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update application
git pull
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Error**: `mysql.connector.errors.InterfaceError: 2003`

**Solutions**:
```bash
# Check if MySQL is running
sudo systemctl status mysql

# Check if port 3306 is open
netstat -tlnp | grep 3306

# Verify user permissions
mysql -u train_user -p
SHOW GRANTS FOR 'train_user'@'localhost';
```

#### 2. Python Import Errors

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solutions**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 3. Permission Denied Errors

**Error**: `PermissionError: [Errno 13] Permission denied`

**Solutions**:
```bash
# Fix file permissions
sudo chown -R trainapp:trainapp /home/trainapp/app
chmod +x app.py

# Check SELinux (CentOS/RHEL)
sudo setsebool -P httpd_can_network_connect 1
```

#### 4. Port Already in Use

**Error**: `OSError: [Errno 98] Address already in use`

**Solutions**:
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>

# Or use different port
export FLASK_RUN_PORT=5001
```

### Log Analysis

#### Application Logs
```bash
# View Flask logs
tail -f /var/log/trainapp/app.log

# View systemd logs
sudo journalctl -u trainapp -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

#### Database Logs
```bash
# MySQL error log
sudo tail -f /var/log/mysql/error.log

# MySQL slow query log
sudo tail -f /var/log/mysql/mysql-slow.log
```

## Maintenance

### Regular Tasks

#### 1. Database Maintenance

```bash
# Backup database
mysqldump -u train_user -p train > backup_$(date +%Y%m%d).sql

# Optimize tables
mysql -u train_user -p train -e "OPTIMIZE TABLE passenger, users, traind, desti, class_coach;"

# Check table integrity
mysql -u train_user -p train -e "CHECK TABLE passenger, users, traind, desti, class_coach;"
```

#### 2. Application Updates

```bash
# Update application code
cd /home/trainapp/app
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart services
sudo systemctl restart trainapp
sudo systemctl restart nginx
```

#### 3. Security Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update SSL certificates
sudo certbot renew

# Review access logs
sudo grep "POST\|PUT\|DELETE" /var/log/nginx/access.log | tail -100
```

#### 4. Performance Monitoring

```bash
# Check system resources
htop
df -h
free -h

# Check application performance
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:5000"

# Monitor database performance
mysql -u train_user -p -e "SHOW PROCESSLIST;"
mysql -u train_user -p -e "SHOW STATUS LIKE 'Threads_%';"
```

### Backup Strategy

#### 1. Automated Database Backups

Create backup script:
```bash
#!/bin/bash
BACKUP_DIR="/home/trainapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/train_backup_$DATE.sql"

mkdir -p $BACKUP_DIR
mysqldump -u train_user -p[PASSWORD] train > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

#### 2. Setup Cron Job

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/trainapp/scripts/backup.sh
```

### Monitoring and Alerts

#### 1. Setup Basic Monitoring

Create monitoring script:
```bash
#!/bin/bash
# Check if application is responding
if ! curl -f -s http://localhost:5000 > /dev/null; then
    echo "Application is down!" | mail -s "Train App Alert" admin@example.com
fi

# Check database connectivity
if ! mysql -u train_user -p[PASSWORD] -e "SELECT 1" > /dev/null 2>&1; then
    echo "Database is down!" | mail -s "Database Alert" admin@example.com
fi
```

#### 2. Log Rotation

Configure logrotate:
```bash
sudo tee /etc/logrotate.d/trainapp << EOF
/var/log/trainapp/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 trainapp trainapp
    postrotate
        systemctl reload trainapp
    endscript
}
EOF
```

This comprehensive deployment guide covers everything from local development setup to production deployment with Docker, monitoring, and maintenance procedures. Follow the sections relevant to your deployment environment and requirements.