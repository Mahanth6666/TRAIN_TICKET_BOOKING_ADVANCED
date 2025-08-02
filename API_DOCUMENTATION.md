# Train Ticket Booking System - API Documentation

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Authentication Routes](#authentication-routes)
  - [User Routes](#user-routes)
  - [Manager Routes](#manager-routes)
  - [General Routes](#general-routes)
- [Database Schema](#database-schema)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)

## Overview

The Train Ticket Booking System is a Flask-based web application that provides a comprehensive platform for managing train reservations. The system supports two user roles: **Customer** and **Manager**, each with different access levels and capabilities.

### Technology Stack
- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS (Tailwind CSS), Jinja2
- **Authentication**: Session-based

## Authentication

The system uses session-based authentication with role-based access control.

### User Roles
- **Customer**: Can book tickets, view train details, and manage their own bookings
- **Manager**: Full administrative access including user management, train management, and destination management

### Authentication Decorator
```python
@requires_roles(*roles)
```
Protects routes that require specific user roles.

## API Endpoints

### Authentication Routes

#### POST `/login`
**Description**: Authenticates a user and creates a session

**Parameters**:
- `username` (string, required): User's username
- `password` (string, required): User's password

**Request Example**:
```html
<form method="POST" action="/login">
    <input type="text" name="username" required>
    <input type="password" name="password" required>
    <button type="submit">Login</button>
</form>
```

**Response**:
- **Success**: Redirects to `/dashboard`
- **Failure**: Returns to login page with error message

**Session Variables Set**:
- `logged_in`: Boolean indicating authentication status
- `username`: Authenticated user's username
- `role`: User's role (customer/manager)

---

#### GET `/logout`
**Description**: Logs out the current user and destroys session

**Authentication**: Required (any authenticated user)

**Response**: Redirects to `/login` with logout confirmation

---

#### POST `/register`
**Description**: Creates a new user account

**Parameters**:
- `username` (string, required): Desired username
- `password` (string, required): User's password
- `role` (string, required): User role ("customer" or "manager")

**Request Example**:
```html
<form method="POST" action="/register">
    <input type="text" name="username" required>
    <input type="password" name="password" required>
    <select name="role" required>
        <option value="customer">Customer</option>
        <option value="manager">Manager</option>
    </select>
    <button type="submit">Register</button>
</form>
```

**Response**:
- **Success**: Redirects to `/login` with success message
- **Failure**: Returns to registration page with error message

---

### User Routes

#### GET `/dashboard`
**Description**: Main dashboard showing role-specific navigation options

**Authentication**: Required (any authenticated user)

**Response**: Renders dashboard with role-appropriate menu items

---

#### POST `/book_ticket`
**Description**: Books a train ticket for a passenger

**Authentication**: Required (any authenticated user)

**Parameters**:
- `class_coach_sno` (int, required): Class coach serial number (1-3)
- `num_tickets` (int, required): Number of tickets to book
- `destination_dno` (int, required): Destination number
- `passenger_name` (string, required): Passenger's full name
- `passenger_age` (string, required): Passenger's age (numeric)
- `phone_number` (string, required): Passenger's phone number (digits only)
- `train_id` (string, required): Train ID (numeric)

**Pricing Structure**:
- **Second Seater** (Class 1): ₹2,000 per ticket
- **Sleeper Class** (Class 2): ₹4,000 per ticket  
- **First Class AC** (Class 3): ₹6,000 per ticket
- **Plus**: Destination-specific additional cost

**Request Example**:
```html
<form method="POST" action="/book_ticket">
    <input type="number" name="class_coach_sno" min="1" max="3" required>
    <input type="number" name="num_tickets" min="1" required>
    <input type="number" name="destination_dno" required>
    <input type="text" name="passenger_name" required>
    <input type="number" name="passenger_age" min="1" required>
    <input type="tel" name="phone_number" pattern="[0-9]+" required>
    <input type="number" name="train_id" required>
    <button type="submit">Book Ticket</button>
</form>
```

**Response**:
- **Success**: Redirects to `/show_passengers` with booking confirmation
- **Failure**: Returns to booking form with validation errors

**Validation Rules**:
- Class coach must be 1-3
- Number of tickets must be positive
- Age must be numeric and positive
- Phone number must contain only digits
- Train ID must be numeric

---

#### GET `/show_passengers`
**Description**: Displays all passenger bookings

**Authentication**: Required (any authenticated user)

**Response**: Renders passenger list with booking details

**Data Returned**:
- Passenger number (pno)
- Name
- Age
- Phone number
- Total cost
- Number of tickets
- Train ID
- Starting point
- Destination
- Registration date

---

#### GET `/show_class_coach`
**Description**: Displays available class coach types and their details

**Authentication**: Required (any authenticated user)

**Response**: Renders class coach information

---

#### GET `/show_train_details`
**Description**: Displays all available trains and their information

**Authentication**: Required (any authenticated user)

**Response**: Renders train listing with details

---

#### GET `/show_destinations`
**Description**: Displays all available destinations and their costs

**Authentication**: Required (any authenticated user)

**Response**: Renders destination listing with pricing

---

### Manager Routes

All manager routes require authentication with `manager` role.

#### DELETE `/delete_passenger/<int:pno>`
**Description**: Deletes a passenger booking

**Authentication**: Required (manager role only)

**Parameters**:
- `pno` (int, URL parameter): Passenger number to delete

**Response**: Redirects to `/show_passengers` with operation result

---

#### POST `/add_train`
**Description**: Adds a new train to the system

**Authentication**: Required (manager role only)

**Parameters**:
- `train_name` (string, required): Name of the train
- `dest1` (string, required): First destination
- `dest2` (string, required): Second destination  
- `dest3` (string, required): Third destination

**Request Example**:
```html
<form method="POST" action="/add_train">
    <input type="text" name="train_name" required>
    <input type="text" name="dest1" required>
    <input type="text" name="dest2" required>
    <input type="text" name="dest3" required>
    <button type="submit">Add Train</button>
</form>
```

**Response**: Redirects to `/show_train_details` with operation result

---

#### POST `/edit_passenger/<int:pno>`
**Description**: Updates passenger information

**Authentication**: Required (manager role only)

**Parameters**:
- `pno` (int, URL parameter): Passenger number to edit
- `name` (string, required): Updated passenger name
- `age` (string, required): Updated age
- `phone` (string, required): Updated phone number

**Response**: Redirects to `/show_passengers` with operation result

---

#### POST `/edit_train/<int:tid>`
**Description**: Updates train information

**Authentication**: Required (manager role only)

**Parameters**:
- `tid` (int, URL parameter): Train ID to edit
- `train_name` (string, required): Updated train name
- `dest1` (string, required): Updated first destination
- `dest2` (string, required): Updated second destination
- `dest3` (string, required): Updated third destination

**Response**: Redirects to `/show_train_details` with operation result

---

#### DELETE `/delete_train/<int:tid>`
**Description**: Deletes a train from the system

**Authentication**: Required (manager role only)

**Parameters**:
- `tid` (int, URL parameter): Train ID to delete

**Safety Check**: Prevents deletion if passengers are booked on the train

**Response**: Redirects to `/show_train_details` with operation result

---

#### POST `/add_destination`
**Description**: Adds a new destination

**Authentication**: Required (manager role only)

**Parameters**:
- `dest_name` (string, required): Destination name
- `cost` (numeric, required): Additional cost for this destination

**Response**: Redirects to `/show_destinations` with operation result

---

#### POST `/edit_destination/<int:dno>`
**Description**: Updates destination information

**Authentication**: Required (manager role only)

**Parameters**:
- `dno` (int, URL parameter): Destination number to edit
- `dest_name` (string, required): Updated destination name
- `cost` (numeric, required): Updated cost

**Response**: Redirects to `/show_destinations` with operation result

---

#### DELETE `/delete_destination/<int:dno>`
**Description**: Deletes a destination

**Authentication**: Required (manager role only)

**Parameters**:
- `dno` (int, URL parameter): Destination number to delete

**Safety Check**: Prevents deletion if passengers have bookings to this destination

**Response**: Redirects to `/show_destinations` with operation result

---

### General Routes

#### GET `/made_by`
**Description**: Shows project information and credits

**Authentication**: Required (any authenticated user)

**Response**: Renders about page with project details

---

#### POST `/forgot_password`
**Description**: Password recovery endpoint (placeholder implementation)

**Parameters**:
- `email` (string, required): User's email address

**Response**: Returns to login with informational message

**Note**: This is a placeholder route - actual password recovery logic needs implementation

---

## Database Schema

### Tables

#### `users`
```sql
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    role ENUM('customer', 'manager') NOT NULL
);
```

#### `passenger`
```sql
CREATE TABLE passenger (
    pno INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    phonenum BIGINT NOT NULL,
    reg_date DATE NOT NULL,
    startingpoint VARCHAR(100) NOT NULL,
    totalcost DECIMAL(10,2) NOT NULL,
    tickets INT NOT NULL,
    tid INT NOT NULL,
    destination VARCHAR(100) NOT NULL
);
```

#### `traind`
```sql
CREATE TABLE traind (
    tid INT AUTO_INCREMENT PRIMARY KEY,
    train_name VARCHAR(100) NOT NULL,
    destination1 VARCHAR(100) NOT NULL,
    destination2 VARCHAR(100) NOT NULL,
    destination3 VARCHAR(100) NOT NULL
);
```

#### `desti`
```sql
CREATE TABLE desti (
    dno INT AUTO_INCREMENT PRIMARY KEY,
    destination VARCHAR(100) NOT NULL,
    cost DECIMAL(10,2) NOT NULL
);
```

#### `class_coach`
```sql
CREATE TABLE class_coach (
    sno INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    base_cost DECIMAL(10,2) NOT NULL
);
```

**Sample Data**:
```sql
INSERT INTO class_coach (class_name, base_cost) VALUES
('Second Seater', 2000.00),
('Sleeper Class', 4000.00),
('First Class AC', 6000.00);
```

## Error Handling

### Flash Message Categories
- **success**: Operation completed successfully (green styling)
- **error**: Operation failed or validation error (red styling)  
- **info**: Informational messages (blue styling)

### Common Error Scenarios
1. **Database Connection Errors**: Handled gracefully with user-friendly messages
2. **Validation Errors**: Input validation with specific error messages
3. **Authorization Errors**: Role-based access control violations
4. **Referential Integrity**: Safety checks prevent deletion of referenced records

### Error Response Format
Errors are displayed using Flask's flash message system and rendered in the frontend with appropriate styling.

## Security Considerations

### ⚠️ Critical Security Issues

1. **Password Storage**: 
   - **Current**: Passwords stored in plain text
   - **Recommendation**: Use `werkzeug.security` or `Flask-Bcrypt` for password hashing
   
2. **SQL Injection Prevention**:
   - **Status**: ✅ Properly implemented using parameterized queries
   - All database queries use parameter binding

3. **Session Security**:
   - **Status**: ✅ Uses `os.urandom(24)` for session secret
   - **Recommendation**: Use environment variables for production

### Recommended Security Improvements

```python
# Password hashing example
from werkzeug.security import generate_password_hash, check_password_hash

# During registration
password_hash = generate_password_hash(password)

# During login
if check_password_hash(user.password_hash, password):
    # Login successful
```

### Input Validation
- Form inputs are validated on the server side
- Numeric inputs checked for appropriate ranges
- Phone numbers validated to contain only digits
- Role-based access control implemented

## Usage Examples

### Customer Workflow
1. Register/Login as customer
2. Access dashboard
3. Book ticket by providing passenger details
4. View booking confirmation
5. Check train and coach details

### Manager Workflow  
1. Login as manager
2. Access administrative dashboard
3. Manage trains (add/edit/delete)
4. Manage destinations (add/edit/delete)
5. Manage passenger bookings (view/edit/delete)
6. View system reports

### API Integration Example

```python
import requests

# Login
session = requests.Session()
login_data = {
    'username': 'admin',
    'password': 'password'
}
response = session.post('http://localhost:5000/login', data=login_data)

# Book a ticket
booking_data = {
    'class_coach_sno': 2,
    'num_tickets': 1,
    'destination_dno': 1,
    'passenger_name': 'John Doe',
    'passenger_age': '30',
    'phone_number': '1234567890',
    'train_id': '1'
}
response = session.post('http://localhost:5000/book_ticket', data=booking_data)
```