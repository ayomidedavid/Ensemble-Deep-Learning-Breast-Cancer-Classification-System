import mysql.connector
from flask import Flask
from app import create_app  # Adjust the import to get the create_app function
app = create_app()  # Create the app instance


def get_db_connection():
    return mysql.connector.connect(
        host=app.config['DATABASE_HOST'],
        user=app.config['DATABASE_USER'],
        password=app.config['DATABASE_PASSWORD'],
        database=app.config['DATABASE_NAME']
    )

def test_db():
    with app.app_context():  # Create application context
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            print(users)
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_db()
