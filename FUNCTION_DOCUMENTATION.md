# Function Documentation - Train Ticket Booking System

## Table of Contents
- [Database Functions](#database-functions)
- [Authentication Functions](#authentication-functions)
- [Utility Functions](#utility-functions)
- [Route Handler Functions](#route-handler-functions)
- [Template Helper Functions](#template-helper-functions)

## Database Functions

### `get_db_connection()`

**Purpose**: Establishes and returns a MySQL database connection

**Parameters**: None

**Returns**: 
- `mysql.connector.connection.MySQLConnection` object on success
- `None` if connection fails

**Usage Example**:
```python
con = get_db_connection()
if con:
    cursor = con.cursor()
    # Perform database operations
    con.close()
```

**Implementation Details**:
```python
def get_db_connection():
    try:
        con = mysql.connect(
            host="localhost",
            user="root",
            password="Mahanth2004",  # Should be in environment variable
            database="train"
        )
        if con.is_connected():
            print("Connected to the database")
        return con
    except mysql.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
```

**Error Handling**:
- Catches `mysql.Error` exceptions
- Prints error message to console
- Returns `None` for failed connections

**Security Notes**:
- ⚠️ Database password is hardcoded (should use environment variables)
- Connection parameters should be configurable

---

## Authentication Functions

### `requires_roles(*roles)`

**Purpose**: Decorator function to enforce role-based access control on routes

**Parameters**:
- `*roles` (tuple): Variable number of allowed roles ('customer', 'manager')

**Returns**: Decorated function with authentication and authorization checks

**Usage Example**:
```python
@app.route('/admin_panel')
@requires_roles('manager')
def admin_panel():
    return render_template('admin.html')

@app.route('/user_or_admin')
@requires_roles('customer', 'manager')
def user_or_admin():
    return render_template('shared.html')
```

**Implementation Details**:
```python
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not session.get('logged_in') or session.get('role') not in roles:
                flash('Unauthorized access.', 'error')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper
```

**Authentication Checks**:
1. Verifies user is logged in (`session.get('logged_in')`)
2. Checks if user's role is in allowed roles list
3. Redirects to login with error message if unauthorized

**Dependencies**:
- `functools.wraps`: Preserves original function metadata
- `flask.session`: For accessing user session data
- `flask.flash`: For displaying error messages
- `flask.redirect` and `flask.url_for`: For redirecting unauthorized users

---

## Route Handler Functions

### Authentication Route Handlers

#### `login()`

**Purpose**: Handles user authentication for both GET and POST requests

**HTTP Methods**: GET, POST

**Authentication Required**: No

**Parameters** (POST only):
- `username` (form field): User's username
- `password` (form field): User's password

**Session Variables Set**:
- `logged_in`: Boolean authentication status
- `username`: Authenticated user's username  
- `role`: User's role from database

**Database Operations**:
```sql
SELECT username, password, role FROM users WHERE username = %s
```

**Security Implementation**:
- Uses parameterized queries to prevent SQL injection
- Password comparison in plain text (⚠️ Security Issue)

**Error Handling**:
- Database connection failures
- Invalid credentials
- MySQL exceptions

**Return Values**:
- **GET**: Renders `login.html` template
- **POST Success**: Redirects to dashboard
- **POST Failure**: Re-renders login with error message

---

#### `register()`

**Purpose**: Handles new user registration

**HTTP Methods**: GET, POST

**Parameters** (POST only):
- `username` (form field): Desired username
- `password` (form field): User's password
- `role` (form field): User role ('customer' or 'manager')

**Database Operations**:
```sql
INSERT INTO users (username, password, role) VALUES (%s, %s, %s)
```

**Validation**:
- No built-in validation (should add username uniqueness check)
- No password strength requirements

**Error Handling**:
- Database connection failures
- Duplicate username errors (MySQL constraint)
- INSERT operation failures

---

#### `logout()`

**Purpose**: Terminates user session and redirects to login

**HTTP Methods**: GET

**Session Operations**:
- Removes `logged_in` session variable
- Removes `role` session variable
- Preserves other session data

**Implementation**:
```python
def logout():
    session.pop('logged_in', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
```

---

### Business Logic Route Handlers

#### `book_ticket()`

**Purpose**: Complex ticket booking workflow with validation and cost calculation

**HTTP Methods**: GET, POST

**Authentication Required**: Yes (any role)

**GET Request Flow**:
1. Establishes database connection
2. Fetches class coaches, destinations, and trains
3. Renders booking form with data

**POST Request Flow**:
1. Validates all input parameters
2. Calculates total cost based on class and destination
3. Inserts passenger record
4. Redirects to passenger list

**Input Validation Rules**:
```python
# Class coach validation
if not (1 <= tic <= len(class_coaches)):
    flash("Invalid class coach selection.", 'error')

# Ticket quantity validation  
if tickets <= 0:
    flash("Number of tickets must be positive.", 'error')

# Age validation
if not age.isdigit() or int(age) <= 0:
    flash("Invalid age, please enter a numeric value.", 'error')

# Phone validation
if not re.match("^\d+$", phonenum):
    flash("Invalid phone number, please enter digits only.", 'error')
```

**Cost Calculation Algorithm**:
```python
# Base cost by class
if tic == 1:      # Second Seater
    tot = 2000 * tickets
elif tic == 2:    # Sleeper Class  
    tot = 4000 * tickets
elif tic == 3:    # First Class AC
    tot = 6000 * tickets

# Add destination cost
tot += tickets * destination_cost
```

**Database Operations**:
```sql
-- Fetch reference data
SELECT * FROM class_coach
SELECT * FROM desti  
SELECT * FROM traind

-- Insert booking
INSERT INTO passenger (name, age, phonenum, reg_date, startingpoint, totalcost, tickets, tid, destination)
VALUES (%s, %s, %s, CURRENT_DATE, %s, %s, %s, %s, %s)
```

**Error Handling**:
- Input validation with specific error messages
- Database connection error handling
- MySQL exception handling
- Value conversion error handling

---

### Data Display Route Handlers

#### `show_passengers()`

**Purpose**: Displays all passenger bookings in tabular format

**Database Query**:
```sql
SELECT pno, name, age, phonenum, totalcost, tickets, tid, startingpoint, destination, reg_date 
FROM passenger
```

**Data Structure**:
Returns list of tuples with passenger information:
- `pno`: Passenger number (primary key)
- `name`: Passenger name
- `age`: Passenger age
- `phonenum`: Phone number
- `totalcost`: Total booking cost
- `tickets`: Number of tickets
- `tid`: Train ID
- `startingpoint`: Origin location
- `destination`: Destination name
- `reg_date`: Registration date

---

#### `show_train_details()`

**Purpose**: Displays all available trains and their destination information

**Database Query**:
```sql
SELECT * FROM traind
```

**Data Fields**:
- `tid`: Train ID
- `train_name`: Train name
- `destination1`: First destination
- `destination2`: Second destination
- `destination3`: Third destination

---

#### `show_destinations()`

**Purpose**: Displays all available destinations with pricing

**Database Query**:
```sql
SELECT * FROM desti
```

**Data Fields**:
- `dno`: Destination number
- `destination`: Destination name
- `cost`: Additional cost for this destination

---

#### `show_class_coach()`

**Purpose**: Displays available coach classes and their information

**Database Query**:
```sql
SELECT * FROM class_coach
```

**Data Fields**:
- `sno`: Serial number
- `class_name`: Coach class name
- `base_cost`: Base cost for this class

---

### Administrative Route Handlers (Manager Only)

#### `delete_passenger(pno)`

**Purpose**: Deletes a passenger booking by passenger number

**Parameters**:
- `pno` (int): Passenger number from URL path

**Authentication Required**: Manager role only

**Database Operations**:
```sql
DELETE FROM passenger WHERE pno = %s
```

**Safety Checks**: None (direct deletion)

**Implementation**:
```python
@app.route('/delete_passenger/<int:pno>')
@requires_roles('manager')
def delete_passenger(pno):
    con = get_db_connection()
    if not con:
        flash('Database connection error.', 'error')
        return redirect(url_for('show_passengers'))

    try:
        cursor = con.cursor()
        sql = "DELETE FROM passenger WHERE pno = %s"
        cursor.execute(sql, (pno,))
        con.commit()
        flash('Passenger deleted successfully.', 'success')
    except mysql.Error as e:
        flash(f"Error deleting passenger: {e}", 'error')
    finally:
        if con.is_connected():
            con.close()
    return redirect(url_for('show_passengers'))
```

---

#### `add_train()`

**Purpose**: Adds a new train to the system

**HTTP Methods**: GET, POST

**Parameters** (POST only):
- `train_name`: Name of the train
- `dest1`: First destination
- `dest2`: Second destination
- `dest3`: Third destination

**Database Operations**:
```sql
INSERT INTO traind (train_name, destination1, destination2, destination3) 
VALUES (%s, %s, %s, %s)
```

**Validation**: Basic form validation only

---

#### `edit_passenger(pno)`

**Purpose**: Updates passenger information

**HTTP Methods**: GET, POST

**GET Request**: Fetches existing passenger data for editing
**POST Request**: Updates passenger information

**Database Operations**:
```sql
-- Fetch for editing
SELECT pno, name, age, phonenum FROM passenger WHERE pno = %s

-- Update passenger
UPDATE passenger SET name = %s, age = %s, phonenum = %s WHERE pno = %s
```

**Validation**: Basic form validation

---

#### `delete_train(tid)`

**Purpose**: Deletes a train with safety checks

**Parameters**:
- `tid` (int): Train ID from URL path

**Safety Check Implementation**:
```python
# Check for existing bookings
sql = "SELECT COUNT(*) FROM passenger WHERE tid = %s"
cursor.execute(sql, (tid,))
count = cursor.fetchone()[0]

if count > 0:
    flash(f'Cannot delete train. There are {count} passengers booked on this train.', 'error')
    return redirect(url_for('show_train_details'))
```

**Database Operations**:
```sql
-- Safety check
SELECT COUNT(*) FROM passenger WHERE tid = %s

-- Delete if safe
DELETE FROM traind WHERE tid = %s
```

---

#### `delete_destination(dno)`

**Purpose**: Deletes a destination with referential integrity check

**Parameters**:
- `dno` (int): Destination number from URL path

**Safety Check Implementation**:
```python
# Check for existing bookings to this destination
sql = "SELECT COUNT(*) FROM passenger WHERE destination = (SELECT destination FROM desti WHERE dno = %s)"
cursor.execute(sql, (dno,))
count = cursor.fetchone()[0]

if count > 0:
    flash(f'Cannot delete destination. There are {count} passengers with bookings to this destination.', 'error')
    return redirect(url_for('show_destinations'))
```

---

## Utility Functions

### Input Validation Helpers

The application uses inline validation within route handlers. Here are the common validation patterns:

#### Age Validation
```python
if not age.isdigit() or int(age) <= 0:
    flash("Invalid age, please enter a numeric value.", 'error')
```

#### Phone Number Validation  
```python
import re
if not re.match("^\d+$", phonenum):
    flash("Invalid phone number, please enter digits only.", 'error')
```

#### Numeric ID Validation
```python
if not tid.isdigit():
    flash("Invalid Train ID, please enter a numeric value.", 'error')
```

#### Range Validation
```python
if not (1 <= tic <= len(class_coaches)):
    flash("Invalid class coach selection.", 'error')
```

### Cost Calculation Utilities

#### Class-Based Pricing
```python
def calculate_class_cost(class_sno, num_tickets):
    """Calculate cost based on class coach selection"""
    base_costs = {1: 2000, 2: 4000, 3: 6000}  # Second Seater, Sleeper, First Class AC
    return base_costs.get(class_sno, 0) * num_tickets
```

#### Destination Cost Addition
```python
def add_destination_cost(base_cost, destination_cost, num_tickets):
    """Add destination-specific cost to base price"""
    return base_cost + (destination_cost * num_tickets)
```

---

## Template Helper Functions

### Flash Message Categories

The application uses Flask's flash messaging system with categorized messages:

```python
# Success messages (green styling)
flash('Operation completed successfully!', 'success')

# Error messages (red styling)  
flash('Error occurred during operation.', 'error')

# Informational messages (blue styling)
flash('Password reset link sent.', 'info')
```

### Session Management Helpers

#### Check Authentication Status
```python
if not session.get('logged_in'):
    return redirect(url_for('login'))
```

#### Role-Based Template Rendering
```python
# In templates
{% if session.role == 'manager' %}
    <!-- Manager-specific content -->
{% else %}
    <!-- Customer content -->
{% endif %}
```

#### Session Variables Access
```python
username = session.get('username')
role = session.get('role')
is_logged_in = session.get('logged_in', False)
```

---

## Error Handling Patterns

### Database Error Handling
```python
try:
    cursor = con.cursor()
    cursor.execute(sql, params)
    con.commit()
    flash('Operation successful', 'success')
except mysql.Error as e:
    flash(f"Database error: {e}", 'error')
finally:
    if con and con.is_connected():
        con.close()
```

### Connection Error Handling
```python
con = get_db_connection()
if not con:
    flash('Database connection error.', 'error')
    return redirect(url_for('dashboard'))
```

### Input Validation Error Handling
```python
try:
    age = int(request.form['age'])
    if age <= 0:
        raise ValueError("Age must be positive")
except ValueError:
    flash("Please enter a valid age.", 'error')
    return render_template('form.html')
```

---

## Performance Considerations

### Database Connection Management
- Connections are opened and closed for each request
- No connection pooling implemented
- Consider implementing connection pooling for production

### Query Optimization
- Simple SELECT queries without joins
- No indexes documented
- Consider adding indexes on frequently queried columns

### Buffered Cursors
```python
xo = con.cursor(buffered=True)  # Used in book_ticket to prevent cursor issues
```

---

## Recommendations for Improvement

### Security Enhancements
1. Implement password hashing using `werkzeug.security`
2. Add CSRF protection
3. Implement rate limiting for login attempts
4. Use environment variables for database credentials

### Validation Improvements
1. Add server-side validation for all inputs
2. Implement client-side validation for better UX
3. Add username uniqueness checking during registration
4. Implement password strength requirements

### Code Organization
1. Separate database operations into a data layer
2. Create separate validation utility functions
3. Implement proper error handling classes
4. Add logging throughout the application

### Database Improvements
1. Add foreign key constraints
2. Implement proper indexing
3. Add audit trails for data changes
4. Consider implementing soft deletes instead of hard deletes