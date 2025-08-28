CREATE DATABASE IF NOT EXISTS finance_db;
USE finance_db;


-- Create users table with name column and user_id column
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    UNIQUE KEY (name)
);

-- Insert values into users table
INSERT INTO users (name)
VALUES 
    ('Tebogo Modiba'),
    ('Karabo Morena'),
    ('Taki Mulaudzi');

-- Financial records table 
CREATE TABLE IF NOT EXISTS financial_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    year INT NOT NULL,
    month VARCHAR(20) NOT NULL,
    amount DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
