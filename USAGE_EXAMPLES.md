# Usage Examples - Train Ticket Booking System

## Table of Contents
- [Getting Started](#getting-started)
- [Customer Workflows](#customer-workflows)
- [Manager Workflows](#manager-workflows)
- [API Integration Examples](#api-integration-examples)
- [Database Operations](#database-operations)
- [Testing Examples](#testing-examples)
- [Common Scenarios](#common-scenarios)
- [Error Handling Examples](#error-handling-examples)

## Getting Started

### Initial Setup and First Login

#### Step 1: Register as a Customer
```bash
# Navigate to the application
curl -X GET http://localhost:5000/register

# Or use browser to access registration form
# Fill in the form with:
# - Username: john_customer
# - Password: password123
# - Role: customer
```

**Registration Form Example:**
```html
<form method="POST" action="/register">
    <input type="text" name="username" value="john_customer" required>
    <input type="password" name="password" value="password123" required>
    <select name="role" required>
        <option value="customer">Customer</option>
    </select>
    <button type="submit">Register</button>
</form>
```

#### Step 2: Login
```bash
# Login with the created credentials
curl -X POST http://localhost:5000/login \
  -d "username=john_customer&password=password123" \
  -c cookies.txt
```

**Expected Response:** Redirect to dashboard with session cookie set.

## Customer Workflows

### Workflow 1: Booking a Single Ticket

#### Complete Ticket Booking Process
```python
import requests

# Create session to maintain cookies
session = requests.Session()

# Step 1: Login
login_data = {
    'username': 'john_customer',
    'password': 'password123'
}
response = session.post('http://localhost:5000/login', data=login_data)
print(f"Login Status: {response.status_code}")

# Step 2: Get booking form data
response = session.get('http://localhost:5000/book_ticket')
print("Available options loaded")

# Step 3: Book a ticket
booking_data = {
    'class_coach_sno': 2,           # Sleeper Class
    'num_tickets': 1,               # One ticket
    'destination_dno': 1,           # First destination from list
    'passenger_name': 'John Doe',
    'passenger_age': '30',
    'phone_number': '9876543210',
    'train_id': '1'                 # First train from list
}

response = session.post('http://localhost:5000/book_ticket', data=booking_data)
print(f"Booking Status: {response.status_code}")

# Step 4: View booking confirmation
response = session.get('http://localhost:5000/show_passengers')
print("Booking confirmed and visible in passenger list")
```

#### Expected Cost Calculation
```python
# For the booking above:
# Class: Sleeper Class (₹4,000)
# Destination: Chennai (₹500) 
# Tickets: 1
# Total = (4000 * 1) + (500 * 1) = ₹4,500
```

### Workflow 2: Booking Multiple Tickets

#### Family Booking Example
```html
<!-- Booking form for family of 3 -->
<form method="POST" action="/book_ticket">
    <select name="class_coach_sno">
        <option value="3">First Class AC - ₹6,000</option>
    </select>
    
    <select name="destination_dno">
        <option value="3">Mumbai - ₹1,200</option>
    </select>
    
    <select name="train_id">
        <option value="1">Shatabdi Express</option>
    </select>
    
    <input type="text" name="passenger_name" value="Johnson Family">
    <input type="number" name="passenger_age" value="35">
    <input type="tel" name="phone_number" value="9876543210">
    <input type="number" name="num_tickets" value="3">
    
    <button type="submit">Book Tickets</button>
</form>
```

**Expected Total Cost:**
```
Class: First Class AC (₹6,000 per ticket)
Destination: Mumbai (₹1,200 per ticket)
Tickets: 3
Total = (6000 * 3) + (1200 * 3) = ₹21,600
```

### Workflow 3: Viewing Available Options

#### Check Available Trains
```python
import requests

session = requests.Session()
# Login first (as shown above)

# Get available trains
response = session.get('http://localhost:5000/show_train_details')
print("Available trains:")
print(response.text)
```

#### Check Class Coaches
```python
# Get class coach information
response = session.get('http://localhost:5000/show_class_coach')
print("Available coach classes:")
print(response.text)
```

#### Check Destinations
```python
# Get destination information
response = session.get('http://localhost:5000/show_destinations')
print("Available destinations:")
print(response.text)
```

## Manager Workflows

### Workflow 1: Complete Train Management

#### Add a New Train
```python
import requests

session = requests.Session()

# Login as manager
login_data = {
    'username': 'admin',
    'password': 'admin123'
}
session.post('http://localhost:5000/login', data=login_data)

# Add new train
train_data = {
    'train_name': 'Garib Rath Express',
    'dest1': 'Coimbatore',
    'dest2': 'Chennai',
    'dest3': 'Bangalore'
}
response = session.post('http://localhost:5000/add_train', data=train_data)
print(f"Train added: {response.status_code}")
```

#### Update Train Information
```python
# Update existing train (assuming train ID = 1)
update_data = {
    'train_name': 'Shatabdi Express (Updated)',
    'dest1': 'Coimbatore',
    'dest2': 'Chennai', 
    'dest3': 'Bangalore'
}
response = session.post('http://localhost:5000/edit_train/1', data=update_data)
print(f"Train updated: {response.status_code}")
```

#### Delete Train (with Safety Check)
```python
# Attempt to delete train
response = session.get('http://localhost:5000/delete_train/1')

# If train has bookings, deletion will be prevented
if response.status_code == 302:  # Redirect with error message
    print("Train deletion prevented - passengers booked")
else:
    print("Train deleted successfully")
```

### Workflow 2: Passenger Management

#### View All Passengers
```python
# Get all passenger bookings
response = session.get('http://localhost:5000/show_passengers')
print("All passenger bookings:")
print(response.text)
```

#### Edit Passenger Information
```python
# Update passenger details (assuming passenger number = 1)
passenger_update = {
    'name': 'John Doe (Updated)',
    'age': '31',
    'phone': '9876543211'
}
response = session.post('http://localhost:5000/edit_passenger/1', data=passenger_update)
print(f"Passenger updated: {response.status_code}")
```

#### Delete Passenger Booking
```python
# Delete a passenger booking
response = session.get('http://localhost:5000/delete_passenger/1')
print(f"Passenger deleted: {response.status_code}")
```

### Workflow 3: Destination Management

#### Add New Destination
```python
# Add a new destination
destination_data = {
    'dest_name': 'Hyderabad',
    'cost': '800'
}
response = session.post('http://localhost:5000/add_destination', data=destination_data)
print(f"Destination added: {response.status_code}")
```

#### Update Destination
```python
# Update destination (assuming destination number = 1)
destination_update = {
    'dest_name': 'Chennai (Updated)',
    'cost': '550'
}
response = session.post('http://localhost:5000/edit_destination/1', data=destination_update)
print(f"Destination updated: {response.status_code}")
```

## API Integration Examples

### Complete Integration Class

```python
class TrainBookingAPI:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.logged_in = False
        
    def login(self, username, password):
        """Login to the system"""
        data = {'username': username, 'password': password}
        response = self.session.post(f"{self.base_url}/login", data=data)
        
        if response.status_code == 200 and 'dashboard' in response.url:
            self.logged_in = True
            return True
        return False
    
    def register(self, username, password, role='customer'):
        """Register a new user"""
        data = {
            'username': username,
            'password': password,
            'role': role
        }
        response = self.session.post(f"{self.base_url}/register", data=data)
        return response.status_code == 302  # Redirect to login
    
    def book_ticket(self, passenger_name, age, phone, class_coach=2, 
                   destination=1, train_id=1, num_tickets=1):
        """Book a train ticket"""
        if not self.logged_in:
            raise Exception("Must be logged in to book tickets")
            
        data = {
            'passenger_name': passenger_name,
            'passenger_age': str(age),
            'phone_number': phone,
            'class_coach_sno': class_coach,
            'destination_dno': destination,
            'train_id': str(train_id),
            'num_tickets': num_tickets
        }
        
        response = self.session.post(f"{self.base_url}/book_ticket", data=data)
        return response.status_code == 302  # Redirect to passengers list
    
    def get_passengers(self):
        """Get all passenger bookings (requires login)"""
        if not self.logged_in:
            raise Exception("Must be logged in")
            
        response = self.session.get(f"{self.base_url}/show_passengers")
        return response.text
    
    def add_train(self, train_name, dest1, dest2, dest3):
        """Add a new train (manager only)"""
        data = {
            'train_name': train_name,
            'dest1': dest1,
            'dest2': dest2,
            'dest3': dest3
        }
        response = self.session.post(f"{self.base_url}/add_train", data=data)
        return response.status_code == 302
    
    def logout(self):
        """Logout from the system"""
        response = self.session.get(f"{self.base_url}/logout")
        self.logged_in = False
        return response.status_code == 302

# Usage example
api = TrainBookingAPI()

# Customer workflow
if api.register("test_user", "password123", "customer"):
    print("Registration successful")
    
if api.login("test_user", "password123"):
    print("Login successful")
    
    # Book a ticket
    if api.book_ticket("Jane Doe", 25, "9876543210", 
                      class_coach=1, destination=2, num_tickets=2):
        print("Ticket booked successfully")
        
    # View bookings
    passengers = api.get_passengers()
    print("Current bookings:", passengers)
    
    api.logout()
```

### Automated Testing Script

```python
def test_complete_workflow():
    """Test complete customer workflow"""
    api = TrainBookingAPI()
    
    # Test registration
    assert api.register("test_customer", "pass123"), "Registration failed"
    
    # Test login
    assert api.login("test_customer", "pass123"), "Login failed"
    
    # Test booking
    assert api.book_ticket(
        passenger_name="Test User",
        age=30,
        phone="1234567890",
        class_coach=2,
        destination=1,
        train_id=1,
        num_tickets=1
    ), "Booking failed"
    
    # Test viewing passengers
    passengers = api.get_passengers()
    assert "Test User" in passengers, "Passenger not found in list"
    
    # Test logout
    assert api.logout(), "Logout failed"
    
    print("All tests passed!")

# Run the test
test_complete_workflow()
```

## Database Operations

### Direct Database Examples

#### Using Python with mysql-connector

```python
import mysql.connector

# Database connection configuration
config = {
    'host': 'localhost',
    'user': 'train_user',
    'password': 'your_password',
    'database': 'train'
}

def get_available_trains():
    """Get all available trains"""
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    query = "SELECT tid, train_name, destination1, destination2, destination3 FROM traind"
    cursor.execute(query)
    
    trains = []
    for (tid, name, dest1, dest2, dest3) in cursor:
        trains.append({
            'id': tid,
            'name': name,
            'destinations': [dest1, dest2, dest3]
        })
    
    cursor.close()
    conn.close()
    return trains

def get_passenger_bookings(start_date=None, end_date=None):
    """Get passenger bookings with optional date filtering"""
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    query = """
        SELECT p.pno, p.name, p.age, p.phonenum, p.totalcost, 
               p.tickets, t.train_name, p.destination, p.reg_date
        FROM passenger p
        JOIN traind t ON p.tid = t.tid
    """
    
    params = []
    if start_date and end_date:
        query += " WHERE p.reg_date BETWEEN %s AND %s"
        params = [start_date, end_date]
    
    query += " ORDER BY p.reg_date DESC"
    
    cursor.execute(query, params)
    
    bookings = []
    for row in cursor:
        bookings.append({
            'passenger_no': row[0],
            'name': row[1],
            'age': row[2],
            'phone': row[3],
            'total_cost': float(row[4]),
            'tickets': row[5],
            'train_name': row[6],
            'destination': row[7],
            'booking_date': row[8].strftime('%Y-%m-%d')
        })
    
    cursor.close()
    conn.close()
    return bookings

def calculate_revenue_by_class():
    """Calculate total revenue by class coach"""
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # This requires cross-referencing with class costs
    query = """
        SELECT 
            CASE 
                WHEN p.totalcost BETWEEN 2000 AND 2999 THEN 'Second Seater'
                WHEN p.totalcost BETWEEN 4000 AND 4999 THEN 'Sleeper Class'
                WHEN p.totalcost >= 6000 THEN 'First Class AC'
            END as class_type,
            SUM(p.totalcost) as total_revenue,
            COUNT(*) as booking_count
        FROM passenger p
        GROUP BY class_type
    """
    
    cursor.execute(query)
    
    revenue_data = []
    for (class_type, revenue, count) in cursor:
        if class_type:  # Filter out None values
            revenue_data.append({
                'class': class_type,
                'revenue': float(revenue),
                'bookings': count
            })
    
    cursor.close()
    conn.close()
    return revenue_data

# Usage examples
trains = get_available_trains()
print("Available trains:", trains)

recent_bookings = get_passenger_bookings('2024-01-01', '2024-12-31')
print("Recent bookings:", recent_bookings)

revenue = calculate_revenue_by_class()
print("Revenue by class:", revenue)
```

### Advanced Database Queries

```sql
-- Get booking statistics by month
SELECT 
    DATE_FORMAT(reg_date, '%Y-%m') as month,
    COUNT(*) as total_bookings,
    SUM(tickets) as total_tickets,
    SUM(totalcost) as total_revenue
FROM passenger 
GROUP BY DATE_FORMAT(reg_date, '%Y-%m')
ORDER BY month DESC;

-- Get most popular destinations
SELECT 
    destination,
    COUNT(*) as booking_count,
    SUM(tickets) as total_tickets,
    AVG(totalcost) as avg_cost
FROM passenger 
GROUP BY destination 
ORDER BY booking_count DESC;

-- Get train utilization
SELECT 
    t.train_name,
    COUNT(p.pno) as total_bookings,
    SUM(p.tickets) as total_passengers,
    SUM(p.totalcost) as total_revenue
FROM traind t
LEFT JOIN passenger p ON t.tid = p.tid
GROUP BY t.tid, t.train_name
ORDER BY total_revenue DESC;

-- Customer analysis
SELECT 
    DATE_FORMAT(reg_date, '%Y-%m') as month,
    COUNT(DISTINCT CONCAT(name, phonenum)) as unique_customers,
    COUNT(*) as total_bookings,
    SUM(totalcost) as revenue
FROM passenger 
GROUP BY DATE_FORMAT(reg_date, '%Y-%m')
ORDER BY month DESC;
```

## Testing Examples

### Unit Testing with pytest

```python
import pytest
import requests
from unittest.mock import Mock, patch
import mysql.connector

class TestTrainBookingSystem:
    @pytest.fixture
    def api_client(self):
        return TrainBookingAPI("http://localhost:5000")
    
    def test_user_registration(self, api_client):
        """Test user registration functionality"""
        # Test successful registration
        result = api_client.register("test_user_001", "password123", "customer")
        assert result == True
        
        # Test duplicate username (should fail)
        result = api_client.register("test_user_001", "password123", "customer")
        assert result == False
    
    def test_login_logout(self, api_client):
        """Test login and logout functionality"""
        # Register first
        api_client.register("test_user_002", "password123", "customer")
        
        # Test successful login
        result = api_client.login("test_user_002", "password123")
        assert result == True
        assert api_client.logged_in == True
        
        # Test logout
        result = api_client.logout()
        assert result == True
        assert api_client.logged_in == False
        
        # Test invalid login
        result = api_client.login("invalid_user", "wrong_password")
        assert result == False
    
    def test_ticket_booking(self, api_client):
        """Test ticket booking functionality"""
        # Setup
        api_client.register("test_user_003", "password123", "customer")
        api_client.login("test_user_003", "password123")
        
        # Test successful booking
        result = api_client.book_ticket(
            passenger_name="Test Passenger",
            age=25,
            phone="1234567890",
            class_coach=1,
            destination=1,
            train_id=1,
            num_tickets=1
        )
        assert result == True
        
        # Verify booking appears in passenger list
        passengers = api_client.get_passengers()
        assert "Test Passenger" in passengers
    
    @patch('mysql.connector.connect')
    def test_database_connection(self, mock_connect):
        """Test database connection handling"""
        # Mock successful connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Test connection function
        from app import get_db_connection
        conn = get_db_connection()
        assert conn is not None
        
        # Test connection failure
        mock_connect.side_effect = mysql.connector.Error("Connection failed")
        conn = get_db_connection()
        assert conn is None

# Integration tests
class TestIntegration:
    def test_full_customer_journey(self):
        """Test complete customer journey"""
        api = TrainBookingAPI()
        
        # Step 1: Registration
        username = f"integration_test_{int(time.time())}"
        assert api.register(username, "password123", "customer")
        
        # Step 2: Login
        assert api.login(username, "password123")
        
        # Step 3: Book multiple tickets
        bookings = [
            {"name": "John Doe", "age": 30, "phone": "1111111111"},
            {"name": "Jane Doe", "age": 28, "phone": "2222222222"}
        ]
        
        for booking in bookings:
            assert api.book_ticket(
                passenger_name=booking["name"],
                age=booking["age"],
                phone=booking["phone"]
            )
        
        # Step 4: Verify all bookings
        passengers = api.get_passengers()
        for booking in bookings:
            assert booking["name"] in passengers
        
        # Step 5: Logout
        assert api.logout()

# Performance tests
class TestPerformance:
    def test_concurrent_bookings(self):
        """Test system under concurrent load"""
        import threading
        import time
        
        results = []
        
        def book_ticket_worker(worker_id):
            api = TrainBookingAPI()
            username = f"perf_test_{worker_id}_{int(time.time())}"
            
            if api.register(username, "password123", "customer"):
                if api.login(username, "password123"):
                    result = api.book_ticket(
                        passenger_name=f"Test User {worker_id}",
                        age=25,
                        phone=f"99999{worker_id:05d}"
                    )
                    results.append(result)
                    api.logout()
        
        # Create 10 concurrent booking threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=book_ticket_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all bookings succeeded
        assert len(results) == 10
        assert all(results)

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## Common Scenarios

### Scenario 1: Peak Time Booking

```python
def simulate_peak_booking():
    """Simulate multiple users booking during peak time"""
    import threading
    import random
    import time
    
    def customer_booking(customer_id):
        api = TrainBookingAPI()
        username = f"customer_{customer_id}"
        
        # Register and login
        api.register(username, "password123", "customer")
        api.login(username, "password123")
        
        # Random booking parameters
        classes = [1, 2, 3]
        destinations = [1, 2, 3, 4, 5]
        trains = [1, 2, 3]
        
        try:
            result = api.book_ticket(
                passenger_name=f"Customer {customer_id}",
                age=random.randint(18, 80),
                phone=f"98765{customer_id:05d}",
                class_coach=random.choice(classes),
                destination=random.choice(destinations),
                train_id=random.choice(trains),
                num_tickets=random.randint(1, 4)
            )
            print(f"Customer {customer_id}: {'Success' if result else 'Failed'}")
        except Exception as e:
            print(f"Customer {customer_id}: Error - {e}")
        finally:
            api.logout()
    
    # Simulate 20 concurrent customers
    threads = []
    for i in range(20):
        thread = threading.Thread(target=customer_booking, args=(i,))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # Stagger the requests slightly
    
    # Wait for all to complete
    for thread in threads:
        thread.join()
    
    print("Peak time simulation completed")

simulate_peak_booking()
```

### Scenario 2: Manager Daily Operations

```python
def manager_daily_operations():
    """Simulate typical manager daily operations"""
    api = TrainBookingAPI()
    
    # Login as manager
    api.login("admin", "admin123")
    
    # Morning: Check overnight bookings
    passengers = api.get_passengers()
    print(f"Overnight bookings: {passengers.count('<tr>')}")
    
    # Add a new train for popular route
    api.add_train(
        train_name="Morning Express",
        dest1="Coimbatore",
        dest2="Chennai",
        dest3="Bangalore"
    )
    
    # Update destination costs based on demand
    # (This would require additional API endpoints)
    
    # Evening: Generate daily report
    # (This would require reporting endpoints)
    
    api.logout()
    print("Manager daily operations completed")

manager_daily_operations()
```

### Scenario 3: System Health Check

```python
def system_health_check():
    """Comprehensive system health check"""
    import time
    import requests
    
    print("Starting system health check...")
    
    # Check 1: Application responsiveness
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print(f"✅ Application responding: {response.status_code}")
    except Exception as e:
        print(f"❌ Application not responding: {e}")
        return False
    
    # Check 2: Database connectivity
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='train_user',
            password='your_password',
            database='train'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        print("✅ Database connectivity: OK")
    except Exception as e:
        print(f"❌ Database connectivity: {e}")
        return False
    
    # Check 3: User registration
    try:
        api = TrainBookingAPI()
        test_user = f"health_check_{int(time.time())}"
        result = api.register(test_user, "password123", "customer")
        print(f"✅ User registration: {'OK' if result else 'Failed'}")
    except Exception as e:
        print(f"❌ User registration: {e}")
    
    # Check 4: Login functionality
    try:
        result = api.login(test_user, "password123")
        print(f"✅ Login functionality: {'OK' if result else 'Failed'}")
    except Exception as e:
        print(f"❌ Login functionality: {e}")
    
    # Check 5: Booking functionality
    try:
        result = api.book_ticket(
            passenger_name="Health Check",
            age=30,
            phone="0000000000"
        )
        print(f"✅ Booking functionality: {'OK' if result else 'Failed'}")
    except Exception as e:
        print(f"❌ Booking functionality: {e}")
    
    print("System health check completed")
    return True

# Run health check
system_health_check()
```

## Error Handling Examples

### Common Error Scenarios and Handling

```python
class TrainBookingAPIWithErrorHandling(TrainBookingAPI):
    def book_ticket_with_validation(self, passenger_name, age, phone, 
                                  class_coach=2, destination=1, train_id=1, num_tickets=1):
        """Book ticket with comprehensive validation and error handling"""
        
        # Input validation
        errors = []
        
        if not passenger_name or len(passenger_name.strip()) < 2:
            errors.append("Passenger name must be at least 2 characters")
        
        if not isinstance(age, int) or age < 1 or age > 120:
            errors.append("Age must be between 1 and 120")
        
        if not str(phone).isdigit() or len(str(phone)) != 10:
            errors.append("Phone number must be 10 digits")
        
        if class_coach not in [1, 2, 3]:
            errors.append("Class coach must be 1, 2, or 3")
        
        if num_tickets < 1 or num_tickets > 10:
            errors.append("Number of tickets must be between 1 and 10")
        
        if errors:
            raise ValueError(f"Validation errors: {'; '.join(errors)}")
        
        # Authentication check
        if not self.logged_in:
            raise Exception("User must be logged in to book tickets")
        
        try:
            # Attempt booking
            data = {
                'passenger_name': passenger_name.strip(),
                'passenger_age': str(age),
                'phone_number': str(phone),
                'class_coach_sno': class_coach,
                'destination_dno': destination,
                'train_id': str(train_id),
                'num_tickets': num_tickets
            }
            
            response = self.session.post(f"{self.base_url}/book_ticket", data=data)
            
            # Check for application-level errors
            if "error" in response.text.lower():
                if "invalid class coach" in response.text.lower():
                    raise ValueError("Selected class coach is not available")
                elif "invalid destination" in response.text.lower():
                    raise ValueError("Selected destination is not available")
                elif "invalid train" in response.text.lower():
                    raise ValueError("Selected train is not available")
                else:
                    raise Exception("Booking failed due to application error")
            
            # Check for successful redirect
            if response.status_code == 302 or "passenger" in response.url:
                return True
            else:
                raise Exception("Booking failed - unexpected response")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error during booking: {e}")
        except Exception as e:
            raise Exception(f"Booking failed: {e}")

# Usage with error handling
def safe_booking_example():
    """Example of safe booking with error handling"""
    api = TrainBookingAPIWithErrorHandling()
    
    try:
        # Login
        if not api.login("test_user", "password123"):
            print("Login failed - please check credentials")
            return
        
        # Attempt booking with validation
        api.book_ticket_with_validation(
            passenger_name="John Doe",
            age=30,
            phone="9876543210",
            class_coach=2,
            destination=1,
            train_id=1,
            num_tickets=2
        )
        print("Booking successful!")
        
    except ValueError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"Booking error: {e}")
    finally:
        if api.logged_in:
            api.logout()

safe_booking_example()
```

### Database Error Handling

```python
def robust_database_operations():
    """Example of robust database operations with error handling"""
    import mysql.connector
    from mysql.connector import Error
    
    config = {
        'host': 'localhost',
        'user': 'train_user',
        'password': 'your_password',
        'database': 'train'
    }
    
    def execute_query_safely(query, params=None):
        """Execute query with comprehensive error handling"""
        conn = None
        cursor = None
        
        try:
            # Establish connection
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            
            # Execute query
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Handle different query types
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return cursor.rowcount
                
        except mysql.connector.InterfaceError as e:
            print(f"Database connection error: {e}")
            return None
        except mysql.connector.ProgrammingError as e:
            print(f"SQL syntax error: {e}")
            return None
        except mysql.connector.IntegrityError as e:
            print(f"Data integrity error: {e}")
            return None
        except mysql.connector.DataError as e:
            print(f"Data error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected database error: {e}")
            return None
        finally:
            # Cleanup
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
    
    # Example usage
    passengers = execute_query_safely(
        "SELECT name, age, totalcost FROM passenger WHERE age > %s",
        (25,)
    )
    
    if passengers is not None:
        print(f"Found {len(passengers)} passengers over 25")
        for name, age, cost in passengers:
            print(f"  {name}, {age} years old, ₹{cost}")
    else:
        print("Failed to retrieve passenger data")

robust_database_operations()
```

This comprehensive usage guide provides practical examples for all major workflows, error handling scenarios, and integration patterns. Users can adapt these examples to their specific needs and requirements.