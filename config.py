import os

class Config:
    SECRET_KEY = 'your_secret_key'
    UPLOAD_FOLDER = 'uploads/'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email@gmail.com'
    MAIL_PASSWORD = 'your_email_password'
    DATABASE_HOST = 'localhost'
    DATABASE_USER = 'root'
    DATABASE_PASSWORD = ''
    DATABASE_NAME = 'batmandiag'  # Placeholder for the actual database name
    # Removed SQLALCHEMY_DATABASE_URI
