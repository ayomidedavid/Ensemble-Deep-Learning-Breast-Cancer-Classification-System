import mysql.connector
from flask import current_app

def get_db_connection():
    return mysql.connector.connect(
        host=current_app.config['DATABASE_HOST'],
        user=current_app.config['DATABASE_USER'],
        password=current_app.config['DATABASE_PASSWORD'],
        database=current_app.config['DATABASE_NAME']
    )

class User:
    def __init__(self, username, email, password, role='user'):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    @staticmethod
    def get_user_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user

class Appointment:
    def __init__(self, user_id, dicom_path):
        self.user_id = user_id
        self.dicom_path = dicom_path
        self.result = None
        self.status = 'Pending'

    @staticmethod
    def get_appointments_by_user(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM appointments WHERE user_id = %s", (user_id,))
        appointments = cursor.fetchall()
        cursor.close()
        conn.close()
        return appointments
