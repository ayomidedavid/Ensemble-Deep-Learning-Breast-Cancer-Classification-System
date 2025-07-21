CREATE DATABASE IF NOT EXISTS batmandiag;

USE batmandiag;

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(200) NOT NULL,
    role ENUM('admin', 'patient', 'consultant') NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL
);

-- Create the appointments table
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    consultant_id INT,
    dicom_path VARCHAR(200) NOT NULL,
    result TEXT,
    reviewed_by_consultant BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (consultant_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Create the appointment_bookings table
CREATE TABLE IF NOT EXISTS appointment_bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    booking_date DATETIME NOT NULL,
    user_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    consultant_id INT NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (consultant_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Add an index to the users table for faster lookups
ALTER TABLE users ADD INDEX (id);

-- Ensure email uniqueness in the users table
ALTER TABLE users ADD UNIQUE (email);

-- Update the foreign key constraints for cascading deletes and nullifying consultant references
ALTER TABLE appointments
    DROP FOREIGN KEY appointments_ibfk_1,
    DROP FOREIGN KEY appointments_ibfk_2;

ALTER TABLE appointments
    ADD CONSTRAINT appointments_ibfk_1 FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    ADD CONSTRAINT appointments_ibfk_2 FOREIGN KEY (consultant_id) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE appointment_bookings
    DROP FOREIGN KEY appointment_bookings_ibfk_1,
    DROP FOREIGN KEY appointment_bookings_ibfk_2,
    DROP FOREIGN KEY appointment_bookings_ibfk_3;

ALTER TABLE appointment_bookings
    ADD CONSTRAINT appointment_bookings_ibfk_1 FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
    ADD CONSTRAINT appointment_bookings_ibfk_2 FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    ADD CONSTRAINT appointment_bookings_ibfk_3 FOREIGN KEY (consultant_id) REFERENCES users(id) ON DELETE SET NULL;

-- Ensure the users table has an index on the id column
ALTER TABLE users ADD INDEX (id);