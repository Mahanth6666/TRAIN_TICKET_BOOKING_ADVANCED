# Database Schema Documentation - Train Ticket Booking System

## Table of Contents
- [Overview](#overview)
- [Database Design](#database-design)
- [Table Definitions](#table-definitions)
- [Relationships](#relationships)
- [Indexes and Constraints](#indexes-and-constraints)
- [Sample Data](#sample-data)
- [Optimization Recommendations](#optimization-recommendations)
- [Migration Scripts](#migration-scripts)

## Overview

The Train Ticket Booking System uses a MySQL database with a simple but effective schema designed to handle user authentication, train management, destination management, and ticket booking operations.

### Database Information
- **Database Name**: `train`
- **Character Set**: `utf8mb4`
- **Collation**: `utf8mb4_unicode_ci`
- **Engine**: InnoDB (recommended)

### Key Features
- Role-based user management
- Train and destination management
- Passenger booking system with cost calculation
- Referential data integrity
- Audit trail capabilities

## Database Design

### Entity Relationship Diagram

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    users    │    │  class_coach│    │    desti    │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ username PK │    │ sno PK      │    │ dno PK      │
│ password    │    │ class_name  │    │ destination │
│ role        │    │ base_cost   │    │ cost        │
│ created_at  │    │ description │    │ created_at  │
│ updated_at  │    └─────────────┘    └─────────────┘
└─────────────┘                            │
                                           │
                    ┌─────────────┐        │
                    │   traind    │        │
                    ├─────────────┤        │
                    │ tid PK      │        │
                    │ train_name  │        │
                    │ destination1│        │
                    │ destination2│        │
                    │ destination3│        │
                    │ created_at  │        │
                    │ updated_at  │        │
                    └─────────────┘        │
                            │              │
                            │              │
                    ┌─────────────┐        │
                    │  passenger  │        │
                    ├─────────────┤        │
                    │ pno PK      │        │
                    │ name        │        │
                    │ age         │        │
                    │ phonenum    │        │
                    │ reg_date    │        │
                    │ startingpoint│       │
                    │ totalcost   │        │
                    │ tickets     │        │
                    │ tid FK      │────────┘
                    │ destination │────────┘
                    │ created_at  │
                    └─────────────┘
```

### Design Principles
1. **Normalization**: Tables are normalized to reduce data redundancy
2. **Referential Integrity**: Foreign key relationships maintain data consistency
3. **Audit Trail**: Timestamps track record creation and updates
4. **Scalability**: Indexed columns for optimal query performance
5. **Data Types**: Appropriate data types for storage efficiency

## Table Definitions

### 1. `users` Table

**Purpose**: Stores user authentication and authorization information

```sql
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    role ENUM('customer', 'manager') NOT NULL DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### Column Details

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| `username` | VARCHAR(50) | PRIMARY KEY | Unique user identifier |
| `password` | VARCHAR(255) | NOT NULL | User password (should be hashed) |
| `role` | ENUM | NOT NULL, DEFAULT 'customer' | User role: 'customer' or 'manager' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| `updated_at` | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update timestamp |

#### Usage Notes
- ⚠️ **Security Issue**: Passwords are currently stored in plain text
- **Recommendation**: Implement password hashing using bcrypt or similar
- Username serves as both identifier and login credential
- Role determines access permissions throughout the application

#### Sample Records
```sql
INSERT INTO users (username, password, role) VALUES
('admin', 'hashed_admin_password', 'manager'),
('john_customer', 'hashed_customer_password', 'customer'),
('jane_manager', 'hashed_manager_password', 'manager');
```

---

### 2. `class_coach` Table

**Purpose**: Defines available train class types and their base costs

```sql
CREATE TABLE class_coach (
    sno INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    base_cost DECIMAL(10,2) NOT NULL,
    description TEXT
);
```

#### Column Details

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| `sno` | INT | PRIMARY KEY, AUTO_INCREMENT | Class serial number |
| `class_name` | VARCHAR(50) | NOT NULL | Display name of the class |
| `base_cost` | DECIMAL(10,2) | NOT NULL | Base cost per ticket for this class |
| `description` | TEXT | NULLABLE | Optional detailed description |

#### Standard Class Types
1. **Second Seater** (sno=1): Basic economy seating - ₹2,000
2. **Sleeper Class** (sno=2): Comfortable berth seating - ₹4,000  
3. **First Class AC** (sno=3): Premium air-conditioned - ₹6,000

#### Sample Records
```sql
INSERT INTO class_coach (class_name, base_cost, description) VALUES
('Second Seater', 2000.00, 'Economy class with basic seating arrangements'),
('Sleeper Class', 4000.00, 'Comfortable sleeper berths for overnight journeys'),
('First Class AC', 6000.00, 'Premium air-conditioned compartment with luxury amenities');
```

---

### 3. `desti` Table

**Purpose**: Manages available destinations and their additional costs

```sql
CREATE TABLE desti (
    dno INT AUTO_INCREMENT PRIMARY KEY,
    destination VARCHAR(100) NOT NULL UNIQUE,
    cost DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Column Details

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| `dno` | INT | PRIMARY KEY, AUTO_INCREMENT | Destination number |
| `destination` | VARCHAR(100) | NOT NULL, UNIQUE | Destination city/location name |
| `cost` | DECIMAL(10,2) | NOT NULL, DEFAULT 0 | Additional cost for this destination |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

#### Business Logic
- Total ticket cost = (Class base cost × number of tickets) + (Destination cost × number of tickets)
- Destination costs vary based on distance and demand
- Unique constraint ensures no duplicate destinations

#### Sample Records
```sql
INSERT INTO desti (destination, cost) VALUES
('Chennai', 500.00),
('Bangalore', 300.00),
('Mumbai', 1200.00),
('Delhi', 2000.00),
('Kolkata', 1500.00),
('Hyderabad', 800.00);
```

---

### 4. `traind` Table

**Purpose**: Stores information about available trains and their routes

```sql
CREATE TABLE traind (
    tid INT AUTO_INCREMENT PRIMARY KEY,
    train_name VARCHAR(100) NOT NULL,
    destination1 VARCHAR(100) NOT NULL,
    destination2 VARCHAR(100) NOT NULL,
    destination3 VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### Column Details

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| `tid` | INT | PRIMARY KEY, AUTO_INCREMENT | Train identifier |
| `train_name` | VARCHAR(100) | NOT NULL | Official train name |
| `destination1` | VARCHAR(100) | NOT NULL | First stop destination |
| `destination2` | VARCHAR(100) | NOT NULL | Second stop destination |
| `destination3` | VARCHAR(100) | NOT NULL | Third stop destination |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update timestamp |

#### Design Notes
- Fixed route structure with exactly 3 destinations per train
- Could be normalized further with separate routes table for flexibility
- Train names should be unique in practice (not enforced by constraint)

#### Sample Records
```sql
INSERT INTO traind (train_name, destination1, destination2, destination3) VALUES
('Shatabdi Express', 'Chennai', 'Bangalore', 'Mumbai'),
('Rajdhani Express', 'Delhi', 'Mumbai', 'Kolkata'),
('Duronto Express', 'Chennai', 'Delhi', 'Bangalore'),
('Garib Rath Express', 'Coimbatore', 'Chennai', 'Bangalore');
```

---

### 5. `passenger` Table

**Purpose**: Records all ticket bookings and passenger information

```sql
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

#### Column Details

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| `pno` | INT | PRIMARY KEY, AUTO_INCREMENT | Passenger number (booking ID) |
| `name` | VARCHAR(100) | NOT NULL | Passenger full name |
| `age` | INT | NOT NULL, CHECK (age > 0 AND age < 150) | Passenger age |
| `phonenum` | BIGINT | NOT NULL | Contact phone number |
| `reg_date` | DATE | NOT NULL | Booking/registration date |
| `startingpoint` | VARCHAR(100) | NOT NULL, DEFAULT 'Coimbatore' | Journey starting location |
| `totalcost` | DECIMAL(10,2) | NOT NULL | Total calculated cost |
| `tickets` | INT | NOT NULL, CHECK (tickets > 0) | Number of tickets booked |
| `tid` | INT | NOT NULL | Foreign key to traind table |
| `destination` | VARCHAR(100) | NOT NULL | Journey destination |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

#### Indexes
- `idx_tid`: Optimizes queries filtering by train ID
- `idx_destination`: Optimizes destination-based queries
- `idx_reg_date`: Optimizes date-based reporting queries

#### Business Rules
1. **Cost Calculation**: `totalcost = (class_base_cost * tickets) + (destination_cost * tickets)`
2. **Default Starting Point**: All journeys start from 'Coimbatore'
3. **Age Validation**: Age must be between 1 and 149
4. **Ticket Validation**: Must book at least 1 ticket

#### Sample Records
```sql
INSERT INTO passenger (name, age, phonenum, reg_date, startingpoint, totalcost, tickets, tid, destination) VALUES
('John Doe', 30, 9876543210, '2024-01-15', 'Coimbatore', 4500.00, 1, 1, 'Chennai'),
('Jane Smith', 28, 9876543211, '2024-01-16', 'Coimbatore', 13200.00, 2, 2, 'Mumbai'),
('Bob Johnson', 45, 9876543212, '2024-01-17', 'Coimbatore', 18600.00, 3, 3, 'Delhi');
```

## Relationships

### Foreign Key Relationships

Although not explicitly defined with foreign key constraints in the current implementation, the following logical relationships exist:

#### 1. passenger.tid → traind.tid
- **Type**: Many-to-One
- **Description**: Multiple passengers can book tickets for the same train
- **Referential Action**: Should prevent train deletion if bookings exist

#### 2. passenger.destination → desti.destination  
- **Type**: Many-to-One
- **Description**: Multiple passengers can travel to the same destination
- **Referential Action**: Should prevent destination deletion if bookings exist

### Relationship Queries

```sql
-- Get passenger bookings with train details
SELECT 
    p.name, p.age, p.tickets, p.totalcost,
    t.train_name, p.destination, p.reg_date
FROM passenger p
JOIN traind t ON p.tid = t.tid
ORDER BY p.reg_date DESC;

-- Get destination booking statistics
SELECT 
    d.destination, d.cost,
    COUNT(p.pno) as total_bookings,
    SUM(p.tickets) as total_passengers,
    SUM(p.totalcost) as total_revenue
FROM desti d
LEFT JOIN passenger p ON d.destination = p.destination
GROUP BY d.dno, d.destination, d.cost
ORDER BY total_revenue DESC;
```

## Indexes and Constraints

### Current Indexes

```sql
-- Primary key indexes (automatically created)
-- users: PRIMARY KEY (username)
-- class_coach: PRIMARY KEY (sno)
-- desti: PRIMARY KEY (dno)
-- traind: PRIMARY KEY (tid)
-- passenger: PRIMARY KEY (pno)

-- Unique indexes
-- desti: UNIQUE KEY (destination)

-- Performance indexes on passenger table
-- INDEX idx_tid (tid)
-- INDEX idx_destination (destination) 
-- INDEX idx_reg_date (reg_date)
```

### Recommended Additional Indexes

```sql
-- For user authentication queries
CREATE INDEX idx_users_role ON users(role);

-- For cost calculation queries
CREATE INDEX idx_class_coach_cost ON class_coach(base_cost);

-- For train search queries
CREATE INDEX idx_traind_name ON traind(train_name);

-- For passenger analytics
CREATE INDEX idx_passenger_cost_date ON passenger(totalcost, reg_date);
CREATE INDEX idx_passenger_phone ON passenger(phonenum);

-- Composite index for common passenger queries
CREATE INDEX idx_passenger_train_dest ON passenger(tid, destination);
```

### Constraints to Add

```sql
-- Add foreign key constraints for data integrity
ALTER TABLE passenger 
ADD CONSTRAINT fk_passenger_train 
FOREIGN KEY (tid) REFERENCES traind(tid) 
ON DELETE RESTRICT ON UPDATE CASCADE;

-- Note: Cannot add FK for destination as it's VARCHAR to VARCHAR
-- Would need to modify schema to use destination ID instead

-- Add check constraints
ALTER TABLE users 
ADD CONSTRAINT chk_username_length 
CHECK (LENGTH(username) >= 3);

ALTER TABLE class_coach 
ADD CONSTRAINT chk_positive_cost 
CHECK (base_cost > 0);

ALTER TABLE desti 
ADD CONSTRAINT chk_destination_length 
CHECK (LENGTH(destination) >= 2);
```

## Sample Data

### Complete Sample Dataset

```sql
-- Sample users
INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'manager'),
('customer1', 'pass123', 'customer'),
('customer2', 'pass456', 'customer'),
('manager1', 'mgr123', 'manager');

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
('Kolkata', 1500.00),
('Hyderabad', 800.00),
('Pune', 1000.00),
('Ahmedabad', 1800.00);

-- Sample trains
INSERT INTO traind (train_name, destination1, destination2, destination3) VALUES
('Shatabdi Express', 'Chennai', 'Bangalore', 'Mumbai'),
('Rajdhani Express', 'Delhi', 'Mumbai', 'Kolkata'),
('Duronto Express', 'Chennai', 'Delhi', 'Bangalore'),
('Garib Rath Express', 'Coimbatore', 'Chennai', 'Hyderabad'),
('Jan Shatabdi', 'Bangalore', 'Chennai', 'Mumbai');

-- Sample passenger bookings
INSERT INTO passenger (name, age, phonenum, reg_date, startingpoint, totalcost, tickets, tid, destination) VALUES
('John Doe', 30, 9876543210, '2024-01-15', 'Coimbatore', 4500.00, 1, 1, 'Chennai'),
('Jane Smith', 28, 9876543211, '2024-01-16', 'Coimbatore', 13200.00, 2, 2, 'Mumbai'),
('Bob Johnson', 45, 9876543212, '2024-01-17', 'Coimbatore', 18600.00, 3, 3, 'Delhi'),
('Alice Brown', 35, 9876543213, '2024-01-18', 'Coimbatore', 5600.00, 2, 1, 'Bangalore'),
('Charlie Wilson', 50, 9876543214, '2024-01-19', 'Coimbatore', 10800.00, 2, 4, 'Hyderabad');
```

## Optimization Recommendations

### Performance Optimizations

#### 1. Index Optimization
```sql
-- Analyze query patterns and add appropriate indexes
EXPLAIN SELECT * FROM passenger WHERE tid = 1 AND reg_date >= '2024-01-01';

-- Add composite indexes for common query patterns
CREATE INDEX idx_passenger_search ON passenger(tid, reg_date, destination);
```

#### 2. Partitioning (for large datasets)
```sql
-- Partition passenger table by date for better performance
ALTER TABLE passenger 
PARTITION BY RANGE(YEAR(reg_date)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);
```

#### 3. Query Optimization
```sql
-- Use covering indexes for frequently accessed columns
CREATE INDEX idx_passenger_covering ON passenger(tid, destination, totalcost, tickets, reg_date);

-- Optimize destination lookup
CREATE INDEX idx_desti_name_cost ON desti(destination, cost);
```

### Schema Improvements

#### 1. Normalize Train Routes
```sql
-- Create separate tables for better normalization
CREATE TABLE routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT NOT NULL,
    destination VARCHAR(100) NOT NULL,
    stop_order INT NOT NULL,
    FOREIGN KEY (train_id) REFERENCES traind(tid)
);
```

#### 2. Add Audit Trail
```sql
-- Add audit columns to critical tables
ALTER TABLE passenger ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
ALTER TABLE passenger ADD COLUMN updated_by VARCHAR(50);
```

#### 3. Implement Soft Deletes
```sql
-- Add deleted_at column for soft deletes
ALTER TABLE traind ADD COLUMN deleted_at TIMESTAMP NULL;
ALTER TABLE desti ADD COLUMN deleted_at TIMESTAMP NULL;
```

### Data Integrity Improvements

```sql
-- Add proper foreign key constraints
ALTER TABLE passenger 
ADD CONSTRAINT fk_passenger_train 
FOREIGN KEY (tid) REFERENCES traind(tid) 
ON DELETE RESTRICT;

-- Add business rule constraints
ALTER TABLE passenger 
ADD CONSTRAINT chk_phone_format 
CHECK (phonenum BETWEEN 1000000000 AND 9999999999);

-- Add unique constraint for business rules
ALTER TABLE passenger 
ADD CONSTRAINT uk_passenger_booking 
UNIQUE (phonenum, tid, reg_date, name);
```

## Migration Scripts

### Initial Database Setup

```sql
-- Create database
CREATE DATABASE train CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE train;

-- Create tables in dependency order
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    role ENUM('customer', 'manager') NOT NULL DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE class_coach (
    sno INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    base_cost DECIMAL(10,2) NOT NULL,
    description TEXT
);

CREATE TABLE desti (
    dno INT AUTO_INCREMENT PRIMARY KEY,
    destination VARCHAR(100) NOT NULL UNIQUE,
    cost DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE traind (
    tid INT AUTO_INCREMENT PRIMARY KEY,
    train_name VARCHAR(100) NOT NULL,
    destination1 VARCHAR(100) NOT NULL,
    destination2 VARCHAR(100) NOT NULL,
    destination3 VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

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

### Version 2.0 Migration (Improvements)

```sql
-- Migration script for enhanced schema
-- Run after backing up existing data

-- Add new columns
ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN email VARCHAR(255) NULL;

ALTER TABLE passenger ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
ALTER TABLE passenger ADD COLUMN booking_status ENUM('confirmed', 'cancelled', 'refunded') DEFAULT 'confirmed';

ALTER TABLE traind ADD COLUMN capacity INT DEFAULT 100;
ALTER TABLE traind ADD COLUMN is_active BOOLEAN DEFAULT TRUE;

-- Add indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_passenger_status ON passenger(booking_status);
CREATE INDEX idx_train_active ON traind(is_active);

-- Add constraints
ALTER TABLE passenger 
ADD CONSTRAINT fk_passenger_train 
FOREIGN KEY (tid) REFERENCES traind(tid) 
ON DELETE RESTRICT;
```

### Rollback Scripts

```sql
-- Rollback script for Version 2.0
ALTER TABLE users DROP COLUMN last_login;
ALTER TABLE users DROP COLUMN email;

ALTER TABLE passenger DROP FOREIGN KEY fk_passenger_train;
ALTER TABLE passenger DROP COLUMN updated_at;
ALTER TABLE passenger DROP COLUMN booking_status;

ALTER TABLE traind DROP COLUMN capacity;
ALTER TABLE traind DROP COLUMN is_active;

DROP INDEX idx_users_email ON users;
DROP INDEX idx_passenger_status ON passenger;
DROP INDEX idx_train_active ON traind;
```

This comprehensive database schema documentation provides a complete understanding of the data structure, relationships, and optimization opportunities for the Train Ticket Booking System.