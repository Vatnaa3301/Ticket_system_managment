-- ============================================================
-- Ticket Management System - Database Schema & Initial Data
-- Database Engine: MySQL / PostgreSQL / SQLite Compatible ANSI SQL
-- ============================================================

-- ------------------------------------------------------------
-- Table: roles
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL,
    description TEXT
);

-- ------------------------------------------------------------
-- Table: auth_user (Django Core User Table)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150) DEFAULT '',
    last_name VARCHAR(150) DEFAULT '',
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL
);

-- ------------------------------------------------------------
-- Table: users (Extended User Profile)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    role_id INT NULL,
    full_name VARCHAR(100) NULL,
    gender VARCHAR(10) NULL,
    phone VARCHAR(20) NULL,
    profile_image VARCHAR(255) NULL,
    department VARCHAR(100) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- Table: ticket_categories
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ticket_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'Active'
);

-- ------------------------------------------------------------
-- Table: priorities
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS priorities (
    priority_id INT AUTO_INCREMENT PRIMARY KEY,
    priority_name VARCHAR(50) NOT NULL,
    response_time_hours INT NOT NULL DEFAULT 24,
    resolution_time_hours INT NOT NULL DEFAULT 48
);

-- ------------------------------------------------------------
-- Table: ticket_statuses
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ticket_statuses (
    status_id INT AUTO_INCREMENT PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL,
    description TEXT,
    `order` INT NOT NULL DEFAULT 0
);

-- ------------------------------------------------------------
-- Table: tickets
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_code VARCHAR(50) NOT NULL UNIQUE,
    subject VARCHAR(200) NOT NULL,
    description TEXT NULL,
    user_id INT NOT NULL,
    category_id INT NULL,
    priority_id INT NULL,
    status_id INT NULL,
    assigned_to_id INT NULL,
    due_date DATE NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    closed_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES ticket_categories(category_id) ON DELETE SET NULL,
    FOREIGN KEY (priority_id) REFERENCES priorities(priority_id) ON DELETE SET NULL,
    FOREIGN KEY (status_id) REFERENCES ticket_statuses(status_id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to_id) REFERENCES auth_user(id) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- Table: ticket_assignments
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ticket_assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    assigned_by_id INT NOT NULL,
    assigned_to_id INT NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    note TEXT NULL,
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Table: ticket_comments
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ticket_comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    comment_text TEXT NOT NULL,
    is_internal BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Table: ticket_attachments
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ticket_attachments (
    attachment_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    uploaded_by_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Table: sla_rules
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sla_rules (
    sla_id INT AUTO_INCREMENT PRIMARY KEY,
    priority_id INT NOT NULL,
    response_time INT NOT NULL,
    resolution_time INT NOT NULL,
    description TEXT NULL,
    FOREIGN KEY (priority_id) REFERENCES priorities(priority_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Table: ticket_logs
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ticket_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    old_value TEXT NULL,
    new_value TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Table: notifications
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ticket_id INT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Table: service_ratings
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS service_ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    rating_score INT NOT NULL,
    feedback TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Table: reports
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    generated_by_id INT NOT NULL,
    report_type VARCHAR(100) NOT NULL,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(255) NULL,
    FOREIGN KEY (generated_by_id) REFERENCES auth_user(id) ON DELETE CASCADE
);


-- ============================================================
-- INITIAL SEED DATA
-- ============================================================

-- 1. Roles
INSERT INTO roles (role_id, role_name, description) VALUES
(1, 'Admin', 'Full system access and admin management'),
(2, 'Support Agent', 'Handles and resolves assigned support tickets'),
(3, 'User', 'Standard user who creates support tickets');

-- 2. Initial Users (auth_user)
INSERT INTO auth_user (id, username, password, first_name, last_name, email, is_staff, is_superuser, is_active, date_joined) VALUES
(1, 'vatana', 'pbkdf2_sha256$password_hash_placeholder', 'Vatana', 'King', 'admin@vatana.com', 1, 1, 1, CURRENT_TIMESTAMP),
(2, 'agent_sarah', 'pbkdf2_sha256$password_hash_placeholder', 'Sarah', 'Agent', 'sarah@vatana.com', 0, 0, 1, CURRENT_TIMESTAMP),
(3, 'john_doe', 'pbkdf2_sha256$password_hash_placeholder', 'John', 'Doe', 'john@vatana.com', 0, 0, 1, CURRENT_TIMESTAMP);

-- 3. Extended User Profiles (users)
INSERT INTO users (id, user_id, role_id, full_name, gender, phone, department, status, created_at) VALUES
(1, 1, 1, 'Vatana King', 'Male', '012345678', 'IT Department', 'Active', CURRENT_TIMESTAMP),
(2, 2, 2, 'Sarah Agent', 'Female', '098765432', 'Technical Support', 'Active', CURRENT_TIMESTAMP),
(3, 3, 3, 'John Doe', 'Male', '011223344', 'Finance Department', 'Active', CURRENT_TIMESTAMP);

-- 4. Categories
INSERT INTO ticket_categories (category_id, category_name, description, status) VALUES
(1, 'Technical Support', 'Hardware, software, and IT support issues', 'Active'),
(2, 'Billing & Accounts', 'Invoicing, subscription, and payment queries', 'Active'),
(3, 'Network & Access', 'VPN, Wi-Fi, permission, and credential access', 'Active');

-- 5. Priorities
INSERT INTO priorities (priority_id, priority_name, response_time_hours, resolution_time_hours) VALUES
(1, 'Low', 48, 96),
(2, 'Medium', 24, 48),
(3, 'High', 4, 12),
(4, 'Critical', 1, 4);

-- 6. Ticket Statuses
INSERT INTO ticket_statuses (status_id, status_name, description, `order`) VALUES
(1, 'To Do', 'Ticket reported and waiting for pick up', 1),
(2, 'In Progress', 'Work actively being performed on ticket', 2),
(3, 'In Review', 'Resolution being tested or reviewed', 3),
(4, 'Done', 'Ticket completed and resolved', 4);

-- 7. SLA Rules
INSERT INTO sla_rules (sla_id, priority_id, response_time, resolution_time, description) VALUES
(1, 1, 48, 96, 'Default SLA for Low Priority'),
(2, 2, 24, 48, 'Default SLA for Medium Priority'),
(3, 3, 4, 12, 'Default SLA for High Priority'),
(4, 4, 1, 4, 'Default SLA for Critical Priority');

-- 8. Sample Tickets
INSERT INTO tickets (ticket_id, ticket_code, subject, description, status_id, priority_id, category_id, user_id, assigned_to_id, created_at, updated_at) VALUES
(1, 'KAN-1', 'Task 1', 'Configure core authentication module and database connection', 1, 3, 1, 3, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 'KAN-2', 'Task 2', 'Implement role-based user permissions and support agent routing', 1, 2, 3, 3, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(3, 'KAN-3', 'Fix VPN Access Disconnection', 'User experiences frequent VPN timeouts during peak hours', 2, 4, 3, 3, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(4, 'KAN-4', 'Billing Invoice Generation Bug', 'PDF invoice export fails when user has non-ASCII characters', 3, 3, 2, 3, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(5, 'KAN-5', 'Upgrade Office Wi-Fi Router Firmware', 'Scheduled router firmware patch for 5th floor network', 4, 1, 1, 1, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
