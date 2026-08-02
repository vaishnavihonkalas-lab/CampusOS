SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS campusos_db;
USE campusos_db;

-- 1. Admins Table
DROP TABLE IF EXISTS admins;
CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'Super Admin',
    avatar_url VARCHAR(255) DEFAULT 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Clubs Table
DROP TABLE IF EXISTS clubs;
CREATE TABLE clubs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    faculty_coordinator VARCHAR(100) DEFAULT 'Dr. S. K. Sharma',
    established_year INT,
    status VARCHAR(20) DEFAULT 'Active',
    logo_url VARCHAR(255) DEFAULT 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=150',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Club Heads Table
DROP TABLE IF EXISTS club_heads;
CREATE TABLE club_heads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL DEFAULT 'head123',
    phone VARCHAR(20),
    club_id INT,
    status VARCHAR(20) DEFAULT 'Active',
    avatar_url VARCHAR(255) DEFAULT 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150',
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Students Table
DROP TABLE IF EXISTS students;
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL DEFAULT 'student123',
    roll_no VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    year VARCHAR(20) NOT NULL,
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Club Members Table
DROP TABLE IF EXISTS club_members;
CREATE TABLE club_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    student_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Approved',
    joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_membership (club_id, student_id),
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- 6. Join Requests Table
DROP TABLE IF EXISTS join_requests;
CREATE TABLE join_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    student_id INT NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- 7. Events Table
DROP TABLE IF EXISTS events;
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    event_time VARCHAR(20) DEFAULT '10:00 AM',
    venue VARCHAR(100) NOT NULL,
    fee DECIMAL(10,2) DEFAULT 0.00,
    capacity INT DEFAULT 100,
    status VARCHAR(20) DEFAULT 'Upcoming',
    poster_url VARCHAR(255) DEFAULT 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=500',
    club_id INT,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Event Registration Table
DROP TABLE IF EXISTS event_registration;
CREATE TABLE event_registration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    student_id INT NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_registration (event_id, student_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- 9. Attendance Table
DROP TABLE IF EXISTS attendance;
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    student_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Present',
    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_attendance (event_id, student_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- 10. Sponsors Table
DROP TABLE IF EXISTS sponsors;
CREATE TABLE sponsors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    company VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    contact VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Confirmed',
    club_id INT,
    event_id INT,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE SET NULL,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Announcements Table
DROP TABLE IF EXISTS announcements;
CREATE TABLE announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
);

-- 12. Certificates Table
DROP TABLE IF EXISTS certificates;
CREATE TABLE certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    student_id INT NOT NULL,
    certificate_code VARCHAR(100) UNIQUE NOT NULL,
    issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- 13. Gallery Table
DROP TABLE IF EXISTS gallery;
CREATE TABLE gallery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    caption VARCHAR(150),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
);

-- 14. Activity Logs Table
DROP TABLE IF EXISTS activity_logs;
CREATE TABLE activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    action VARCHAR(255) NOT NULL,
    module VARCHAR(50) NOT NULL,
    ip_address VARCHAR(50) DEFAULT '127.0.0.1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. Settings Table
DROP TABLE IF EXISTS settings;
CREATE TABLE settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL
);

-- 16. Notifications Table
DROP TABLE IF EXISTS notifications;
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    target_role VARCHAR(50) DEFAULT 'All',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ========================================================
-- SEED DATA
-- ========================================================

INSERT INTO admins (id, name, email, password, role) VALUES 
(1, 'Super Admin', 'admin@campusos.edu', 'admin123', 'Super Admin');

INSERT INTO clubs (id, name, category, description, faculty_coordinator, established_year, status) VALUES 
(1, 'Turing Coding Club', 'Technical', 'Official competitive programming, web dev, and open-source hackathon society.', 'Dr. Rajesh Verma', 2017, 'Active'),
(2, 'RoboTech Innovation Society', 'Technical', 'IoT, Robotics, Autonomous Drones, and Hardware innovation lab.', 'Prof. Anitha Rao', 2018, 'Active'),
(3, 'Nataraj Cultural Club', 'Cultural', 'Promoting classical, fusion dance and dramatic arts on campus.', 'Dr. Sunita Kapoor', 2016, 'Active'),
(4, 'E-Cell Entrepreneurship', 'Management', 'Nurturing student startups, venture capital pitches, and business summits.', 'Prof. Vikram Joshi', 2020, 'Active');

INSERT INTO club_heads (id, name, email, password, phone, club_id, status) VALUES 
(1, 'Aarav Sharma', 'aarav.sharma@campusos.edu', 'head123', '9876543210', 1, 'Active'),
(2, 'Ananya Iyer', 'ananya.iyer@campusos.edu', 'head123', '9876543211', 2, 'Active'),
(3, 'Rohan Verma', 'rohan.verma@campusos.edu', 'head123', '9876543212', 3, 'Active'),
(4, 'Priya Nair', 'priya.nair@campusos.edu', 'head123', '9876543213', 4, 'Active');

INSERT INTO students (id, name, email, password, roll_no, department, year, phone, status) VALUES 
(1, 'John Doe', 'john@student.edu', 'student123', '21BCS1001', 'Computer Science & Engg', '3rd Year', '9123456780', 'Active'),
(2, 'Rahul Gupta', 'rahul.g@student.edu', 'student123', '22BIT1042', 'Information Technology', '2nd Year', '9823411223', 'Active'),
(3, 'Ishita Chakraborty', 'ishita.c@student.edu', 'student123', '21ECE2015', 'Electronics & Comm Engg', '3rd Year', '9711223344', 'Active'),
(4, 'Arjun Mehta', 'arjun.m@student.edu', 'student123', '23ADS1088', 'AI & Data Science', '1st Year', '9988776655', 'Active'),
(5, 'Diya Joshi', 'diya.j@student.edu', 'student123', '20BME1005', 'Mechanical Engineering', '4th Year', '9845012345', 'Active');

INSERT INTO club_members (club_id, student_id, status) VALUES 
(1, 1, 'Approved'), (1, 2, 'Approved'), (1, 4, 'Approved'), (2, 3, 'Approved'), (3, 5, 'Approved');

INSERT INTO events (id, title, description, event_date, event_time, venue, fee, capacity, status, club_id) VALUES 
(1, 'HackKritrim 2026 AI Hackathon', 'National 24-hour AI hackathon.', '2026-09-15', '09:00 AM', 'Visvesvaraya Auditorium', 0.00, 150, 'Approved', 1),
(2, 'RoboKriti Bot Championship', 'Bot combat tournament in open arena.', '2026-10-02', '11:00 AM', 'Ramanujan Tech Grounds', 200.00, 60, 'Approved', 2),
(3, 'Tarang Cultural Fest', 'Inter-college dance and music fest.', '2026-10-20', '05:00 PM', 'Main Open Air Theatre', 0.00, 300, 'Approved', 3);

INSERT INTO event_registration (event_id, student_id) VALUES 
(1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (3, 5);

INSERT INTO sponsors (id, name, company, amount, contact, phone, email, status, club_id, event_id) VALUES 
(1, 'Tata Consultancy Services', 'TCS Labs', 250000.00, 'Vikram Malhotra', '9811223344', 'campus@tcs.com', 'Confirmed', 1, 1),
(2, 'Infosys Springboard', 'Infosys Ltd', 150000.00, 'Priya Sengupta', '9822334455', 'outreach@infosys.com', 'Confirmed', 1, 1),
(3, 'Swiggy Campus Lead', 'Swiggy', 80000.00, 'Rohan Das', '9833445566', 'marketing@swiggy.in', 'Confirmed', 3, 3);

INSERT INTO activity_logs (user_name, action, module, ip_address) VALUES 
('Super Admin', 'System Initialized & Seeded Data Uploaded', 'System', '127.0.0.1'),
('Super Admin', 'Approved HackKritrim 2026 AI Hackathon', 'Events', '127.0.0.1'),
('Aarav Sharma', 'Posted Announcement for Turing Coding Club', 'Announcements', '127.0.0.1');

INSERT INTO settings (setting_key, setting_value) VALUES 
('college_name', 'National Institute of Technology & Science'),
('academic_year', '2026-2027'),
('max_clubs', '20'),
('max_members', '500'),
('password_policy', 'Strong (Min 8 Chars, Numbers & Symbols)'),
('theme', 'Dark SaaS');

SET FOREIGN_KEY_CHECKS = 1;