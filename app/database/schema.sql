-- Face Recognition Attendance System Database Schema
-- For XAMPP MySQL

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS face_recognition_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE face_recognition_db;

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE NOT NULL COMMENT 'Student ID/Code',
    name VARCHAR(100) NOT NULL COMMENT 'Full Name',
    email VARCHAR(100) UNIQUE COMMENT 'Email Address',
    phone VARCHAR(20) COMMENT 'Phone Number',
    course VARCHAR(100) COMMENT 'Course/Program',
    year_level INT COMMENT 'Year Level',
    section VARCHAR(20) COMMENT 'Section',
    status ENUM(
        'active',
        'inactive',
        'graduated'
    ) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id),
    INDEX idx_name (name),
    INDEX idx_status (status)
);

-- Face encodings table
CREATE TABLE IF NOT EXISTS face_encodings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    encoding_data LONGTEXT NOT NULL COMMENT 'Face encoding as JSON string',
    image_path VARCHAR(500) COMMENT 'Path to reference image',
    confidence_score DECIMAL(5, 4) DEFAULT 1.0000 COMMENT 'Encoding confidence score',
    is_primary BOOLEAN DEFAULT FALSE COMMENT 'Primary encoding for student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    INDEX idx_student_id (student_id),
    INDEX idx_is_primary (is_primary)
);

-- Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL COMMENT 'Attendance timestamp',
    method ENUM(
        'face_recognition',
        'manual',
        'api'
    ) DEFAULT 'face_recognition',
    confidence_score DECIMAL(5, 4) COMMENT 'Recognition confidence score',
    location VARCHAR(100) COMMENT 'Location where attendance was marked',
    device_info TEXT COMMENT 'Device information',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    UNIQUE KEY unique_daily_attendance (student_id, DATE(timestamp)),
    INDEX idx_student_id (student_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_date (DATE(timestamp))
);

-- Attendance sessions table
CREATE TABLE IF NOT EXISTS attendance_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_name VARCHAR(100) NOT NULL COMMENT 'Session name/description',
    start_time TIMESTAMP NOT NULL COMMENT 'Session start time',
    end_time TIMESTAMP COMMENT 'Session end time',
    status ENUM(
        'active',
        'completed',
        'cancelled'
    ) DEFAULT 'active',
    created_by VARCHAR(100) COMMENT 'Who created the session',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_start_time (start_time)
);

-- Session attendance table (for multiple sessions per day)
CREATE TABLE IF NOT EXISTS session_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    student_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL COMMENT 'Attendance timestamp',
    status ENUM(
        'present',
        'late',
        'absent',
        'excused'
    ) DEFAULT 'present',
    notes TEXT COMMENT 'Additional notes',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES attendance_sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    UNIQUE KEY unique_session_attendance (session_id, student_id),
    INDEX idx_session_id (session_id),
    INDEX idx_student_id (student_id)
);

-- System logs table
CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level ENUM(
        'INFO',
        'WARNING',
        'ERROR',
        'DEBUG'
    ) DEFAULT 'INFO',
    message TEXT NOT NULL,
    source VARCHAR(100) COMMENT 'Source of the log entry',
    user_id VARCHAR(100) COMMENT 'User who triggered the action',
    ip_address VARCHAR(45) COMMENT 'IP address',
    user_agent TEXT COMMENT 'User agent string',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_level (level),
    INDEX idx_created_at (created_at),
    INDEX idx_source (source)
);

-- Settings table
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT COMMENT 'Setting value (can be JSON)',
    description TEXT COMMENT 'Setting description',
    category VARCHAR(50) DEFAULT 'general' COMMENT 'Setting category',
    is_editable BOOLEAN DEFAULT TRUE COMMENT 'Whether setting can be edited',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_setting_key (setting_key)
);

-- Insert default settings
INSERT IGNORE INTO
    settings (
        setting_key,
        setting_value,
        description,
        category
    )
VALUES (
        'face_recognition_threshold',
        '0.6',
        'Face recognition confidence threshold',
        'recognition'
    ),
    (
        'camera_fps',
        '30',
        'Camera frames per second',
        'camera'
    ),
    (
        'attendance_cooldown',
        '3',
        'Seconds between attendance marks for same student',
        'attendance'
    ),
    (
        'max_unknown_faces',
        '100',
        'Maximum unknown faces to track',
        'recognition'
    ),
    (
        'export_format',
        'csv',
        'Default export format',
        'export'
    ),
    (
        'database_backup_enabled',
        'true',
        'Enable automatic database backups',
        'system'
    ),
    (
        'backup_retention_days',
        '30',
        'Days to keep backup files',
        'system'
    );

-- Create views for common queries
CREATE OR REPLACE VIEW attendance_summary AS
SELECT
    DATE(a.timestamp) as date,
    COUNT(DISTINCT a.student_id) as present_count,
    (
        SELECT COUNT(*)
        FROM students
        WHERE
            status = 'active'
    ) as total_students,
    ROUND(
        (
            COUNT(DISTINCT a.student_id) / (
                SELECT COUNT(*)
                FROM students
                WHERE
                    status = 'active'
            )
        ) * 100,
        2
    ) as attendance_rate
FROM attendance a
WHERE
    a.timestamp >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY
    DATE(a.timestamp)
ORDER BY date DESC;

-- Create stored procedure for marking attendance
DELIMITER /
/

CREATE PROCEDURE MarkAttendance(
    IN p_student_id INT,
    IN p_timestamp TIMESTAMP,
    IN p_method ENUM('face_recognition', 'manual', 'api') DEFAULT 'face_recognition',
    IN p_confidence_score DECIMAL(5,4) DEFAULT NULL,
    IN p_location VARCHAR(100) DEFAULT NULL
)
BEGIN
    DECLARE v_attendance_id INT;
    
    -- Insert or update attendance
    INSERT INTO attendance (student_id, timestamp, method, confidence_score, location)
    VALUES (p_student_id, p_timestamp, p_method, p_confidence_score, p_location)
    ON DUPLICATE KEY UPDATE
        timestamp = VALUES(timestamp),
        method = VALUES(method),
        confidence_score = VALUES(confidence_score),
        location = VALUES(location),
        updated_at = CURRENT_TIMESTAMP;
    
    -- Get the attendance ID
    SET v_attendance_id = LAST_INSERT_ID();
    
    -- Log the action
    INSERT INTO system_logs (level, message, source, user_id)
    VALUES ('INFO', CONCAT('Attendance marked for student ID: ', p_student_id), 'attendance_system', 'system');
    
    -- Return success
    SELECT v_attendance_id as attendance_id, 'success' as status;
END
/
/

DELIMITER;

-- Create indexes for better performance
CREATE INDEX idx_attendance_date_student ON attendance (DATE(timestamp), student_id);

CREATE INDEX idx_face_encodings_student_primary ON face_encodings (student_id, is_primary);

CREATE INDEX idx_students_status_created ON students (status, created_at);

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON face_recognition_db.* TO 'your_user'@'localhost';
-- FLUSH PRIVILEGES;