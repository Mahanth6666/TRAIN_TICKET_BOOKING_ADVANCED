from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector as mysql
import re
import os
from functools import wraps

app = Flask(__name__)
# Set a secret key for session management. In a real application, use a strong, randomly generated key.
app.secret_key = os.urandom(24) 

# --- Database Connection ---
# Establish connection to MySQL
def get_db_connection():
    try:
        con = mysql.connect(
            host="localhost",
            user="root",
            password="Mahanth2004",
            database="train"
        )
        if con.is_connected():
            print("Connected to the database")
        return con
    except mysql.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# --- Authentication ---
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

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        con = get_db_connection()
        if not con:
            flash('Database connection error.', 'error')
            return redirect(url_for('login'))

        try:
            cursor = con.cursor()
            sql = "SELECT username, password, role FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()

            if user and user[1] == password:  # In production, use proper password hashing
                session['logged_in'] = True
                session['username'] = username
                session['role'] = user[2]
                flash('Authentication successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials, please try again.', 'error')
        except mysql.Error as e:
            flash(f"Error during login: {e}", 'error')
        finally:
            if con.is_connected():
                con.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- Registration ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        con = get_db_connection()
        if not con:
            flash('Database connection error.', 'error')
            return redirect(url_for('register'))

        try:
            cursor = con.cursor()
            sql = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, password, role))
            con.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.Error as e:
            flash(f"Error during registration: {e}", 'error')
        finally:
            if con.is_connected():
                con.close()

    return render_template('register.html')

# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# --- Ticket Booking ---
@app.route('/book_ticket', methods=['GET', 'POST'])
def book_ticket():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    con = get_db_connection()
    if not con:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))

    try:
        xo = con.cursor(buffered=True) # Use buffered=True to fetch all results before other queries

        # Fetch class coaches
        s = "SELECT * FROM class_coach"
        xo.execute(s)
        class_coaches = xo.fetchall()

        # Fetch destinations
        s = "SELECT * FROM desti"
        xo.execute(s)
        destinations = xo.fetchall()

        # Fetch trains
        s = "SELECT * FROM traind"
        xo.execute(s)
        trains = xo.fetchall()

        if request.method == 'POST':
            try:
                # Get data from form
                tic = int(request.form['class_coach_sno'])
                tickets = int(request.form['num_tickets'])
                ddd = int(request.form['destination_dno'])
                name = request.form['passenger_name']
                age = request.form['passenger_age']
                phonenum = request.form['phone_number']
                tid = request.form['train_id']

                # Input validation
                if not (1 <= tic <= len(class_coaches)):
                    flash("Invalid class coach selection.", 'error')
                    return render_template('book_ticket.html', class_coaches=class_coaches, destinations=destinations, trains=trains)
                if tickets <= 0:
                    flash("Number of tickets must be positive.", 'error')
                    return render_template('book_ticket.html', class_coaches=class_coaches, destinations=destinations, trains=trains)
                if not (1 <= ddd <= len(destinations)): # Assuming DNo starts from 1 and is sequential
                    flash("Invalid destination selection.", 'error')
                    return render_template('book_ticket.html', class_coaches=class_coaches, destinations=destinations, trains=trains)
                if not age.isdigit() or int(age) <= 0:
                    flash("Invalid age, please enter a numeric value.", 'error')
                    return render_template('book_ticket.html', class_coaches=class_coaches, destinations=destinations, trains=trains)
                if not re.match("^\d+$", phonenum):
                    flash("Invalid phone number, please enter digits only.", 'error')
                    return render_template('book_ticket.html', class_coaches=class_coaches, destinations=destinations, trains=trains)
                if not tid.isdigit():
                    flash("Invalid Train ID, please enter a numeric value.", 'error')
                    return render_template('book_ticket.html', class_coaches=class_coaches, destinations=destinations, trains=trains)

                # Calculate total cost based on class coach
                tot = 0
                if tic == 1: # Assuming SNo 1 is Second Seater
                    tot = 2000 * tickets
                elif tic == 2: # Assuming SNo 2 is Sleeper Class
                    tot = 4000 * tickets
                elif tic == 3: # Assuming SNo 3 is First Class AC
                    tot = 6000 * tickets
                else:
                    flash("Invalid class coach selection.", 'error')
                    return render_template('book_ticket.html', class_coaches=class_coaches, destinations=destinations, trains=trains)

                # Get selected destination cost
                selected_destination_info = next((d for d in destinations if d[0] == ddd), None)
                if selected_destination_info:
                    selected_destination_name = selected_destination_info[1]
                    destination_cost = selected_destination_info[2]
                    tot += tickets * destination_cost
                else:
                    flash("Selected destination not found.", 'error')
                    return render_template('book_ticket.html', class_coaches=class_coaches, destinations=destinations, trains=trains)

                startingpoint = "Coimbatore" # Default value as in original script

                # Prepare data for insertion
                passenger_data = (
                    name,
                    int(age),
                    int(phonenum),
                    startingpoint,
                    tot,
                    tickets,
                    int(tid),
                    selected_destination_name
                )

                # Insert into passenger table
                sql = """
                    INSERT INTO passenger (name, age, phonenum, reg_date, startingpoint, totalcost, tickets, tid, destination)
                    VALUES (%s, %s, %s, CURRENT_DATE, %s, %s, %s, %s, %s)
                """
                xo.execute(sql, passenger_data)
                con.commit()

                flash(f"Ticket booked and passenger added successfully! Total bill: Rs {tot}", 'success')
                return redirect(url_for('show_passengers')) # Redirect to show all passengers after booking

            except ValueError:
                flash("Please enter valid numeric values for age, phone number, tickets, and IDs.", 'error')
            except mysql.Error as e:
                flash(f"Error during ticket booking: {e}", 'error')
            finally:
                if con.is_connected():
                    con.close()

        return render_template('book_ticket.html', class_coaches=class_coaches, destinations=destinations, trains=trains)

    except mysql.Error as e:
        flash(f"Error fetching data for booking: {e}", 'error')
        return redirect(url_for('dashboard'))
    finally:
        if con and con.is_connected():
            con.close()

# --- Show All Passengers ---
@app.route('/show_passengers')
def show_passengers():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    con = get_db_connection()
    if not con:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))

    passengers = []
    try:
        xo = con.cursor()
        s = "SELECT pno, name, age, phonenum, totalcost, tickets, tid, startingpoint, destination, reg_date FROM passenger"
        xo.execute(s)
        passengers = xo.fetchall()
    except mysql.Error as e:
        flash(f"Error fetching passenger details: {e}", 'error')
    finally:
        if con.is_connected():
            con.close()
    return render_template('show_passengers.html', passengers=passengers)

# --- Show Class Coach Details ---
@app.route('/show_class_coach')
def show_class_coach():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    con = get_db_connection()
    if not con:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))

    class_coaches = []
    try:
        xo = con.cursor()
        s = "SELECT * FROM class_coach"
        xo.execute(s)
        class_coaches = xo.fetchall()
    except mysql.Error as e:
        flash(f"Error fetching class coach details: {e}", 'error')
    finally:
        if con.is_connected():
            con.close()
    return render_template('show_class_coach.html', class_coaches=class_coaches)

# --- Show Train Details ---
@app.route('/show_train_details')
def show_train_details():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    con = get_db_connection()
    if not con:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))

    trains = []
    try:
        xo = con.cursor()
        s = "SELECT * FROM traind"
        xo.execute(s)
        trains = xo.fetchall()
    except mysql.Error as e:
        flash(f"Error fetching train details: {e}", 'error')
    finally:
        if con.is_connected():
            con.close()
    return render_template('show_train_details.html', trains=trains)


# --- Made By ---
@app.route('/made_by')
def made_by_web():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    msg = '''
        Train Ticket Booking System           :
        Roll No                             : 86
        School Name                         : PSG TECH
        Session                             : 2024
        
        Thanks for evaluating my Project.
    '''
    return render_template('made_by.html', message=msg)

# --- Forgot Password ---
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Add logic to handle password reset, e.g., sending a reset link to the user's email
        flash('If the email exists in our system, a password reset link has been sent.', 'info')
        return redirect(url_for('login'))

    return render_template('forgot_password.html')

# Add manager-specific routes
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

@app.route('/add_train', methods=['GET', 'POST'])
@requires_roles('manager')
def add_train():
    if request.method == 'POST':
        train_name = request.form['train_name']
        dest1 = request.form['dest1']
        dest2 = request.form['dest2']
        dest3 = request.form['dest3']

        con = get_db_connection()
        if not con:
            flash('Database connection error.', 'error')
            return redirect(url_for('show_train_details'))

        try:
            cursor = con.cursor()
            sql = "INSERT INTO traind (train_name, destination1, destination2, destination3) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (train_name, dest1, dest2, dest3))
            con.commit()
            flash('Train added successfully.', 'success')
            return redirect(url_for('show_train_details'))
        except mysql.Error as e:
            flash(f"Error adding train: {e}", 'error')
        finally:
            if con.is_connected():
                con.close()

    return render_template('add_train.html')

@app.route('/edit_passenger/<int:pno>', methods=['GET', 'POST'])
@requires_roles('manager')
def edit_passenger(pno):
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        phone = request.form['phone']

        con = get_db_connection()
        if not con:
            flash('Database connection error.', 'error')
            return redirect(url_for('show_passengers'))

        try:
            cursor = con.cursor()
            sql = "UPDATE passenger SET name = %s, age = %s, phonenum = %s WHERE pno = %s"
            cursor.execute(sql, (name, age, phone, pno))
            con.commit()
            flash('Passenger details updated successfully.', 'success')
            return redirect(url_for('show_passengers'))
        except mysql.Error as e:
            flash(f"Error updating passenger: {e}", 'error')
        finally:
            if con.is_connected():
                con.close()

    con = get_db_connection()
    if not con:
        flash('Database connection error.', 'error')
        return redirect(url_for('show_passengers'))

    try:
        cursor = con.cursor()
        sql = "SELECT pno, name, age, phonenum FROM passenger WHERE pno = %s"
        cursor.execute(sql, (pno,))
        passenger = cursor.fetchone()
        if not passenger:
            flash('Passenger not found.', 'error')
            return redirect(url_for('show_passengers'))
    except mysql.Error as e:
        flash(f"Error fetching passenger details: {e}", 'error')
        return redirect(url_for('show_passengers'))
    finally:
        if con.is_connected():
            con.close()

    return render_template('edit_passenger.html', passenger=passenger)

# Add train management routes
@app.route('/edit_train/<int:tid>', methods=['GET', 'POST'])
@requires_roles('manager')
def edit_train(tid):
    if request.method == 'POST':
        train_name = request.form['train_name']
        dest1 = request.form['dest1']
        dest2 = request.form['dest2']
        dest3 = request.form['dest3']

        con = get_db_connection()
        if not con:
            flash('Database connection error.', 'error')
            return redirect(url_for('show_train_details'))

        try:
            cursor = con.cursor()
            sql = """
                UPDATE traind 
                SET train_name = %s, destination1 = %s, destination2 = %s, destination3 = %s 
                WHERE tid = %s
            """
            cursor.execute(sql, (train_name, dest1, dest2, dest3, tid))
            con.commit()
            flash('Train details updated successfully.', 'success')
            return redirect(url_for('show_train_details'))
        except mysql.Error as e:
            flash(f"Error updating train: {e}", 'error')
        finally:
            if con.is_connected():
                con.close()

    con = get_db_connection()
    if not con:
        flash('Database connection error.', 'error')
        return redirect(url_for('show_train_details'))

    try:
        cursor = con.cursor()
        sql = "SELECT * FROM traind WHERE tid = %s"
        cursor.execute(sql, (tid,))
        train = cursor.fetchone()
        if not train:
            flash('Train not found.', 'error')
            return redirect(url_for('show_train_details'))
    except mysql.Error as e:
        flash(f"Error fetching train details: {e}", 'error')
        return redirect(url_for('show_train_details'))
    finally:
        if con.is_connected():
            con.close()

    return render_template('edit_train.html', train=train)

@app.route('/delete_train/<int:tid>')
@requires_roles('manager')
def delete_train(tid):
    con = get_db_connection()
    if not con:
        flash('Database connection error.', 'error')
        return redirect(url_for('show_train_details'))

    try:
        # First check if there are any passengers booked on this train
        cursor = con.cursor()
        sql = "SELECT COUNT(*) FROM passenger WHERE tid = %s"
        cursor.execute(sql, (tid,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            flash(f'Cannot delete train. There are {count} passengers booked on this train.', 'error')
            return redirect(url_for('show_train_details'))

        sql = "DELETE FROM traind WHERE tid = %s"
        cursor.execute(sql, (tid,))
        con.commit()
        flash('Train deleted successfully.', 'success')
    except mysql.Error as e:
        flash(f"Error deleting train: {e}", 'error')
    finally:
        if con.is_connected():
            con.close()
    return redirect(url_for('show_train_details'))

# --- Show Destinations ---
@app.route('/show_destinations')
def show_destinations():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    con = get_db_connection()
    if not con:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))

    destinations = []
    try:
        cursor = con.cursor()
        sql = "SELECT * FROM desti"
        cursor.execute(sql)
        destinations = cursor.fetchall()
    except mysql.Error as e:
        flash(f"Error fetching destination details: {e}", 'error')
    finally:
        if con.is_connected():
            con.close()
    return render_template('show_destinations.html', destinations=destinations)

@app.route('/add_destination', methods=['GET', 'POST'])
@requires_roles('manager')
def add_destination():
    if request.method == 'POST':
        dest_name = request.form['dest_name']
        cost = request.form['cost']

        con = get_db_connection()
        if not con:
            flash('Database connection error.', 'error')
            return redirect(url_for('show_destinations'))

        try:
            cursor = con.cursor()
            sql = "INSERT INTO desti (destination, cost) VALUES (%s, %s)"
            cursor.execute(sql, (dest_name, cost))
            con.commit()
            flash('Destination added successfully.', 'success')
            return redirect(url_for('show_destinations'))
        except mysql.Error as e:
            flash(f"Error adding destination: {e}", 'error')
        finally:
            if con.is_connected():
                con.close()

    return render_template('edit_destination.html')

@app.route('/edit_destination/<int:dno>', methods=['GET', 'POST'])
@requires_roles('manager')
def edit_destination(dno):
    if request.method == 'POST':
        dest_name = request.form['dest_name']
        cost = request.form['cost']

        con = get_db_connection()
        if not con:
            flash('Database connection error.', 'error')
            return redirect(url_for('show_destinations'))

        try:
            cursor = con.cursor()
            sql = "UPDATE desti SET destination = %s, cost = %s WHERE dno = %s"
            cursor.execute(sql, (dest_name, cost, dno))
            con.commit()
            flash('Destination updated successfully.', 'success')
            return redirect(url_for('show_destinations'))
        except mysql.Error as e:
            flash(f"Error updating destination: {e}", 'error')
        finally:
            if con.is_connected():
                con.close()

    con = get_db_connection()
    if not con:
        flash('Database connection error.', 'error')
        return redirect(url_for('show_destinations'))

    try:
        cursor = con.cursor()
        sql = "SELECT * FROM desti WHERE dno = %s"
        cursor.execute(sql, (dno,))
        destination = cursor.fetchone()
        if not destination:
            flash('Destination not found.', 'error')
            return redirect(url_for('show_destinations'))
    except mysql.Error as e:
        flash(f"Error fetching destination details: {e}", 'error')
        return redirect(url_for('show_destinations'))
    finally:
        if con.is_connected():
            con.close()

    return render_template('edit_destination.html', destination=destination)

@app.route('/delete_destination/<int:dno>')
@requires_roles('manager')
def delete_destination(dno):
    con = get_db_connection()
    if not con:
        flash('Database connection error.', 'error')
        return redirect(url_for('show_destinations'))

    try:
        # First check if there are any passengers booked with this destination
        cursor = con.cursor()
        sql = "SELECT COUNT(*) FROM passenger WHERE destination = (SELECT destination FROM desti WHERE dno = %s)"
        cursor.execute(sql, (dno,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            flash(f'Cannot delete destination. There are {count} passengers with bookings to this destination.', 'error')
            return redirect(url_for('show_destinations'))

        sql = "DELETE FROM desti WHERE dno = %s"
        cursor.execute(sql, (dno,))
        con.commit()
        flash('Destination deleted successfully.', 'success')
    except mysql.Error as e:
        flash(f"Error deleting destination: {e}", 'error')
    finally:
        if con.is_connected():
            con.close()
    return redirect(url_for('show_destinations'))

if __name__ == '__main__':
    app.run(debug=True) # debug=True allows for automatic reloading and provides debugging information