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

## Usability Evaluation Summary
Usability Evaluation: Development of an Ensemble-Based Deep Learning System for Breast Cancer Detection from Mammography and Magnetic Resonance Imaging Modalities  
This usability evaluation summarizes the system's functionality and user experience. Testing was conducted with two participant groups: medical professionals (acting as consultants/radiologists) and patients, to gather structured feedback on key aspects such as ease of use, clarity of instructions, and technical performance. The system is designed to support breast cancer detection using mammography and MRI modalities.

**Medical Professionals Usability Evaluation**  
Medical professionals reported a highly positive experience with the system, with most rating its usability between 4 and 5 (Very Easy) across key functions:  
Login and User Management (Q1: 4.5/5) and Patient Request Handling (Q2: 4.6/5) were seamless.  
Image Upload & Review (Q4: 4.7/5) had the highest efficiency.  
System Interface Friendliness (Q7: 4.4/5) was very good, and System Speed (Q6: 4.6/5) was consistently rated as fast.  
Calculations:  
Overall Average Score = (4.5 + 4.6 + 4.5 + 4.7 + 4.5 + 4.6 + 4.4 + 4.5) / 8 = 4.55/5  
Usability Percentage = (4.55 / 5) × 100 = 91%

**Patients Usability Evaluation**  
Patients rated the system 4.1/5 overall, indicating good usability with room for improvement:  
Appointment Booking (Q3: 4.3/5) and Interface Design (Q6: 4.2/5) were strengths.  
Seamless appointment process (Q4: 3.9/5) and Feedback Clarity (Q5: 4.0/5) needed refinement.  
Calculations:  
Overall Average Score = (4.2 + 4.1 + 4.3 + 3.9 + 4.0 + 4.1 + 4.2 + 4.1) / 8 = 4.11/5  
Usability Percentage = (4.11 / 5) × 100 = 82%

**Comparative Summary**

| Category                   | Medical Professionals | Patients | Remarks                                         |
|----------------------------|----------------------|----------|-------------------------------------------------|
| Overall Average Score      | 4.55 / 5             | 4.11 / 5 | Medical professionals rated the system higher overall. |
| Usability Percentage       | 91%                  | 82%      | Higher perceived usability from the professional side. |
| Top-Rated Feature          | Image Upload & Review (4.7/5) | Appointment Booking (4.3/5) | Professionals praised workflow efficiency; patients liked scheduling ease. |
| System Speed (Q6)          | 4.6 / 5              | 4.2 / 5  | Rated fast by both groups; slightly better from the professional side. |
| Interface Friendliness/Design | 4.4 / 5           | 4.2 / 5  | Positive feedback from both groups.             |
| Login (Q1)                 | 4.5 / 5              | 4.2/ 5   | Seamless access for both professionals and patients. |
| Patient Request Handling (Q2) | 4.6 / 5           | —        | Strong backend support noted by professionals.  |
| Appointment Process (Q4)   | —                    | 3.9 / 5  | Patients reported this as an area needing improvement. |
| Feedback Clarity (Q5)      | —                    | 4.0 / 5  | Lowest-rated patient feature; improvement recommended. |

The ensemble system scored an impressive 4.3/5 overall in usability testing. Most patients found it easy to navigate, especially for booking appointments (4.3/5) and viewing results (4.2/5). While the interface design scored well (4.2/5), some professionals reported minor difficulties with file uploads (3.9/5) and wanted clearer instructions. The system's speed was fast (4.1/5), and technical issues were rare.

## License
This project is for educational and research purposes.
# Ensemble-Deep-Learning-Breast-Cancer-Classification-System
