import socket
from flask import Flask, request, flash, redirect, url_for, render_template
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy  # <-- Add this import
from config import Config

app = Flask(__name__)

# Initialize SQLAlchemy instance here
db = SQLAlchemy()

bcrypt = Bcrypt()
mail = Mail()
socketio = SocketIO()

def get_local_ip():
    """Fetch the local IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external server to determine the local IP
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = 'your_secret_key'  # Replace with a secure key

    # Ensure SQLALCHEMY_DATABASE_URI is set
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    db.init_app(app)

    bcrypt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)

    from routes import main  # Import AFTER app initialization
    app.register_blueprint(main)

    return app

# Import only Appointment from models
from models import Appointment

@app.route('/prediction/<int:appointment_id>', methods=['GET', 'POST'])
def prediction(appointment_id):
    from flask import current_app
    appointment = Appointment.query.get_or_404(appointment_id)
    if request.method == 'POST':
        print("Form data:", request.form)
        if 'edited_result' in request.form:
            new_result = request.form['edited_result']
            print("Editing result to:", new_result)
            # Explicitly update and flush the session
            appointment.result = new_result
            db.session.flush()
            db.session.commit()
            flash('Result updated successfully!', 'success')
            return redirect(url_for('prediction', appointment_id=appointment.id))
        elif 'dicom_file' in request.files:
            # ...handle DICOM upload...
            pass
    return render_template('prediction.html', appointment=appointment)

if __name__ == '__main__':
    app = create_app()
    local_ip = get_local_ip()
    print(f"App is running! Access it on your network at: http://{local_ip}:5000")
    print("Press CTRL+C to stop the server.")
    # Bind to all interfaces (0.0.0.0) to make the app accessible on the network
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
