# Development of an Ensemble-Based Deep Learning System for Breast Cancer Detection from Mammography and Magnetic Resonance Imaging Modalities

## Project Overview
This project implements an ensemble-based deep learning system to assist in the detection of breast cancer using mammography and MRI modalities. The system provides secure user management, image upload and review, appointment booking, and role-based dashboards for medical professionals and patients.

## Features
- Secure login and registration for multiple user roles (admin, medical professional, patient)
- Mammography and MRI image upload and review
- Appointment booking and management
- Role-based dashboards and navigation
- Usability-focused interface
- Fast system performance
- Feedback and result clarity
- Admin management tools

## Folder Structure
- `app.py` - Main Flask application
- `models.py` - Database models
- `routes.py` - Application routes
- `config.py` - Configuration settings
- `templates/` - HTML templates for all pages
- `static/` - Static files (CSS, images, uploads)
- `instance/database.db` - SQLite database
- `models/` - Deep learning models (H5, PTH)
- `uploads/` - DICOM and image uploads
- `sql/` - SQL scripts

## Setup Instructions
1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialize the database:**
   - Run the SQL scripts in `sql/` and `create_database.sql` as needed
4. **Start the Flask app:**
   ```bash
   flask run
   ```
5. **Access the system:**
   - Open your browser and go to `http://localhost:5000`

## Usage
- Register or log in as a medical professional or patient
- Upload mammography or MRI images and review results
- Book and manage appointments
- Use dashboards for role-specific features

## Admin Credentials
- **Username:** `admin`
- **Email:** `admin@example.com`
- **Password:** `admin_password`

## License
This project is for educational and research purposes.
# Ensemble-Deep-Learning-Breast-Cancer-Classification-System
