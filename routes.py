import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_socketio import SocketIO
from models import User, Appointment, get_db_connection  # Import get_db_connection from models
import os
from werkzeug.utils import secure_filename
import pydicom
import numpy as np
import tensorflow as tf
import torch
from torchvision import transforms
from PIL import Image
import time
from mysql.connector.errors import DatabaseError

bcrypt = Bcrypt()
mail = Mail()
socketio = SocketIO()

main = Blueprint('main', __name__)

def check_user_in_database(username, email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    existing_user = cursor.fetchone()
    cursor.close()
    conn.close()
    return existing_user

def insert_user_into_database(user):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                   (user.username, user.email, user.password, user.role))
    conn.commit()
    cursor.close()
    conn.close()

def insert_consultant_into_database(consultant):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                   (consultant.username, consultant.email, consultant.password, consultant.role))
    conn.commit()
    cursor.close()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'dcm'}

def is_valid_dicom(file_path):
    try:
        pydicom.dcmread(file_path)
        return True
    except Exception:
        return False

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        
        # Check for existing user
        existing_user = check_user_in_database(username, email)

        if existing_user:
            flash('Username or email already exists. Please choose another.', 'danger')
            return redirect(url_for('main.register'))

        try:
            user = User(username=username, email=email, password=password, role='patient')
            insert_user_into_database(user)

            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            logging.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('main.register'))
    return render_template('register.html')

@main.route('/register_consultant', methods=['GET', 'POST'])
def register_consultant():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        try:
            consultant = User(username=username, email=email, password=password, role='consultant')
            insert_consultant_into_database(consultant)

            flash('Consultant registration successful. Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('main.register_consultant'))
    return render_template('register_consultant.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = check_user_in_database(None, email)  # Use the existing function to get user data
        if user and bcrypt.check_password_hash(user['password'], password):
            if user['role'] != 'patient':  # Prevent consultants from logging in as patients
                flash('Unauthorized access for this role.', 'danger')
                return redirect(url_for('main.login'))
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['username'] = user['username']  # Store the username in the session
            return redirect(url_for('main.dashboard'))

        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@main.route('/login_consultant', methods=['GET', 'POST'])
def login_consultant():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND role = 'consultant'", (email,))
        consultant = cursor.fetchone()
        cursor.close()
        conn.close()

        if consultant and bcrypt.check_password_hash(consultant['password'], password):
            session['user_id'] = consultant['id']
            session['username'] = consultant['username']  # Store the consultant's name
            session['logged_in'] = True  # Mark the user as logged in
            session['role'] = 'consultant'  # Store the role
            flash('Login successful!', 'success')
            return redirect(url_for('main.medical_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login_consultant.html')

@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    # Fetch the patient's name from the session
    patient_name = session.get('username', 'Patient')
    
    # Fetch available consultants
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username FROM users WHERE role = 'consultant'")
    consultants = cursor.fetchall()

    # Handle appointment booking form submission
    if request.method == 'POST':
        consultant_id = request.form['consultant_id']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']

        # Insert into the `appointments` table first
        cursor.execute("""
            INSERT INTO appointments (user_id, consultant_id, dicom_path, result, reviewed_by_consultant)
            VALUES (%s, %s, '', NULL, FALSE)
        """, (session['user_id'], consultant_id))
        conn.commit()

        # Get the newly created appointment ID
        appointment_id = cursor.lastrowid

        # Insert into the `appointment_bookings` table
        cursor.execute("""
            INSERT INTO appointment_bookings (appointment_id, booking_date, user_id, appointment_date, appointment_time, consultant_id, status)
            VALUES (%s, NOW(), %s, %s, %s, %s, 'Pending')
        """, (appointment_id, session['user_id'], appointment_date, appointment_time, consultant_id))
        conn.commit()

        flash('Appointment booked successfully!', 'success')  # Add success message
        return redirect(url_for('main.dashboard'))

    # Fetch test results for the logged-in patient
    cursor.execute("""
        SELECT ab.appointment_date, ab.appointment_time, ab.booking_date, ab.consultant_id, ab.status,
               u.username AS consultant_name, a.result, a.dicom_path
        FROM appointment_bookings ab
        JOIN users u ON ab.consultant_id = u.id
        JOIN appointments a ON ab.appointment_id = a.id
        WHERE ab.user_id = %s
    """, (session['user_id'],))
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('dashboard.html', patient_name=patient_name, consultants=consultants, appointments=appointments)

from PIL import Image

@main.route('/upload', methods=['POST'])
def upload_dicom():
    if 'dicom_file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('main.dashboard'))
    file = request.files['dicom_file']
    filename = secure_filename(file.filename)
    filepath = os.path.join('uploads', filename)
    file.save(filepath)

    # Convert DICOM to PNG
    try:
        dicom_data = pydicom.dcmread(filepath)
        pixel_array = dicom_data.pixel_array
        image = Image.fromarray(pixel_array)
        png_filename = os.path.splitext(filename)[0] + '.png'
        png_filepath = os.path.join('static/uploads', png_filename)
        image.save(png_filepath)

        # Normalize the path to use forward slashes
        relative_png_path = os.path.relpath(png_filepath, 'static').replace('\\', '/')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO appointments (user_id, dicom_path) VALUES (%s, %s)", (session['user_id'], relative_png_path))
        conn.commit()
        cursor.close()
        conn.close()

        flash('File uploaded and converted successfully.', 'success')
        return redirect(url_for('main.prediction_page', appointment_id=cursor.lastrowid))
    except Exception as e:
        flash(f'Error processing DICOM file: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

@main.route('/process/<int:appointment_id>')
def process_dicom(appointment_id):
    appointment = Appointment.get_appointment_by_id(appointment_id)
    model = tf.keras.models.load_model('model.h5')
    dicom_data = pydicom.dcmread(appointment['dicom_path']).pixel_array
    dicom_data = np.expand_dims(dicom_data, axis=0)
    result = model.predict(dicom_data)
    appointment['result'] = f'AI Prediction: Cancer Probability: {result[0][0] * 100:.2f}%'
    appointment['status'] = 'Awaiting Review'
    Appointment.update_appointment(appointment)
    flash('AI has processed the image. Waiting for medical expert review.', 'info')
    return redirect(url_for('main.dashboard'))

@main.route('/edit_result/<int:appointment_id>', methods=['GET', 'POST'])
def edit_result(appointment_id):
    if 'user_id' not in session or session['role'] != 'medical_expert':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main.dashboard'))

    appointment = Appointment.get_appointment_by_id(appointment_id)
    
    if request.method == 'POST':
        edited_result = request.form['result']
        appointment['result'] = edited_result
        appointment['status'] = 'Finalized'
        appointment['practitioner_id'] = session['user_id']
        Appointment.update_appointment(appointment)

        # Send Finalized Results to User via Email
        msg = Message('Your Final Test Results', sender='your_email@gmail.com', recipients=[appointment['user_email']])
        msg.body = f'Your final reviewed test results: {appointment['result']}'
        mail.send(msg)

        # Send Real-Time Notification
        socketio.emit('new_notification', {'message': 'Your final test result is ready!'}, room=appointment['user_id'])

        flash('Result updated and sent to user successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('edit_result.html', appointment=appointment)

@main.route('/test_db', methods=['GET'])
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return {'users': users}, 200
    except Exception as e:
        return {'error': str(e)}, 500

@main.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Check admin credentials
        if email == 'admin@example.com' and password == 'admin_password':  # Example credentials
            session['user_id'] = 'admin'  # Set a session variable for admin
            session['role'] = 'admin'  # Set the role to admin
            session['username'] = 'Admin'  # Set the username for display
            flash('Login successful!', 'success')
            return redirect(url_for('main.admin_dashboard'))  # Redirect to admin dashboard
        flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')

@main.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all patients
    cursor.execute("SELECT id, username, email FROM users WHERE role = 'patient'")
    patients = cursor.fetchall()

    # Fetch all consultants
    cursor.execute("SELECT id, username, email FROM users WHERE role = 'consultant'")
    consultants = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html', patients=patients, consultants=consultants)

@main.route('/medical_dashboard')
def medical_dashboard():
    if 'user_id' not in session or session.get('role') != 'consultant':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.login_consultant'))
    
    # Fetch consultant's name
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
    consultant = cursor.fetchone()

    # Fetch appointments for the logged-in consultant
    cursor.execute("""
        SELECT ab.appointment_date, ab.appointment_time, ab.booking_date, ab.user_id, ab.status,
               u.username AS patient_name, a.result, ab.id AS appointment_booking_id, a.id AS appointment_id
        FROM appointment_bookings ab
        JOIN users u ON ab.user_id = u.id
        JOIN appointments a ON ab.appointment_id = a.id
        WHERE ab.consultant_id = %s
    """, (session['user_id'],))
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('medical_dashboard.html', consultant_name=consultant['username'], appointments=appointments)

@main.route('/accept_appointment/<int:appointment_booking_id>', methods=['GET'])
def accept_appointment(appointment_booking_id):
    if 'user_id' not in session or session.get('role') != 'consultant':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.login_consultant'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appointment_bookings
        SET status = 'Accepted'
        WHERE id = %s
    """, (appointment_booking_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Appointment accepted successfully!', 'success')
    return redirect(url_for('main.medical_dashboard'))

@main.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login_consultant'))

@main.route('/prediction/<int:appointment_id>', methods=['GET', 'POST'])
def prediction_page(appointment_id):
    if 'user_id' not in session or session.get('role') != 'consultant':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.login_consultant'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, u.username AS patient_name
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        WHERE a.id = %s
    """, (appointment_id,))
    appointment = cursor.fetchone()
    cursor.close()
    conn.close()

    if not appointment:
        flash('Appointment not found!', 'danger')
        return redirect(url_for('main.medical_dashboard'))

    # Automatically load the PNG path for display
    png_path = url_for('static', filename=appointment['dicom_path'])
    print(f"Debug: png_path = {png_path}")  # Debug log

    return render_template('prediction.html', appointment=appointment, png_path=png_path)

@main.route('/admin_reset_password/<int:user_id>', methods=['POST'])
def admin_reset_password(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    new_password = request.form.get('new_password')
    if not new_password:
        flash('Password cannot be empty!', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Password reset successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/toggle_user_status/<int:user_id>', methods=['POST'])
def toggle_user_status(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    retries = 3
    for attempt in range(retries):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Fetch the current active status of the user
            cursor.execute("SELECT active FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            if not user:
                flash('User not found!', 'danger')
                return redirect(url_for('main.admin_dashboard'))

            # Toggle the active status
            new_status = not user['active']
            cursor.execute("UPDATE users SET active = %s WHERE id = %s", (new_status, user_id))
            conn.commit()

            cursor.close()
            conn.close()

            status_message = 'enabled' if new_status else 'disabled'
            flash(f'User account has been {status_message} successfully!', 'success')
            return redirect(url_for('main.admin_dashboard'))
        except DatabaseError as e:
            if "1205" in str(e):  # Lock wait timeout
                if attempt < retries - 1:
                    time.sleep(2)  # Wait before retrying
                    continue
                else:
                    flash('Database error: Lock wait timeout exceeded. Please try again later.', 'danger')
                    return redirect(url_for('main.admin_dashboard'))
            else:
                raise

@main.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if the user has associated records in appointment_bookings
    cursor.execute("SELECT COUNT(*) AS count FROM appointment_bookings WHERE user_id = %s", (user_id,))
    booking_count = cursor.fetchone()['count']

    if booking_count > 0:
        flash('Cannot delete user. The user has associated appointments.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('main.admin_dashboard'))

    # Proceed with deletion if no associated records
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash('User account has been deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))  # Fixed missing closing parenthesis

@main.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            # Generate a password reset link (dummy link for now)
            reset_link = f"http://{request.host}/reset_password/{user['id']}"
            # Send email with the reset link
            msg = Message('Password Reset Request', sender='your_email@gmail.com', recipients=[email])
            msg.body = f"Click the link to reset your password: {reset_link}"
            mail.send(msg)
            flash('A password reset link has been sent to your email.', 'info')
        else:
            flash('No account found with that email.', 'danger')

        return redirect(url_for('main.forgot_password'))

    return render_template('forgot_password.html')


# The user self-service reset function is retained, and the admin reset function is now correctly named.


@main.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile.', 'danger')
        return redirect(url_for('main.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        cursor.execute("UPDATE users SET username = %s, email = %s WHERE id = %s", (username, email, session['user_id']))
        conn.commit()
        flash('Profile updated successfully.', 'success')

    cursor.execute("SELECT username, email FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('profile.html', user=user)
