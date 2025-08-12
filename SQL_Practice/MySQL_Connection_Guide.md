# 🗄️ MySQL Connection Setup Guide

## Step 1: Start MySQL Server (XAMPP)
1. **Open XAMPP Control Panel** (should be running now)
2. **Click "Start" next to MySQL**
3. **Wait for green "Running" status**

## Step 2: Create Connection in VS Code

### Method A: Using VS Code MySQL Extension

1. **Open VS Code**
2. **Click the MySQL extension icon** in the left sidebar (database icon)
3. **Click the "+" button** to add new connection
4. **Enter these connection details:**

```
Connection Name: Local MySQL
Host: 127.0.0.1 (or localhost)
Port: 3306
Username: root
Password: (leave empty - default XAMPP has no password)
```

5. **Click "Connect"**

### Method B: Using Command Palette

1. **Press Ctrl+Shift+P** (Command Palette)
2. **Type "MySQL: Add Connection"**
3. **Enter the same details as above**

## Step 3: Test Your Connection

Once connected, you should see:
- **Database tree** in the MySQL panel
- **Default databases** like `information_schema`, `mysql`, `performance_schema`

## Step 4: Create Your First Database

Right-click in the MySQL panel and select:
- **"New Database"**
- **Name it:** `practice_db`

## Common Connection Settings for XAMPP:

| Setting | Value |
|---------|-------|
| Host | `127.0.0.1` or `localhost` |
| Port | `3306` |
| Username | `root` |
| Password | *(empty)* |
| Database | *(optional)* |

## Troubleshooting:

### ❌ "Cannot connect to server"
- **Check XAMPP:** MySQL must be "Running" (green)
- **Check Port:** Make sure port 3306 is free
- **Restart XAMPP:** Stop and start MySQL in XAMPP

### ❌ "Access denied"
- **Username:** Use `root`
- **Password:** Leave empty for default XAMPP
- **Check XAMPP config:** Some versions might have a password

### ❌ "Connection timeout"
- **Firewall:** Check Windows firewall settings
- **Antivirus:** Some antivirus blocks database connections

## Next Steps: Practice SQL

Once connected, try these basic commands:

```sql
-- Create a database
CREATE DATABASE my_practice;

-- Use the database
USE my_practice;

-- Create a table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    email VARCHAR(100)
);

-- Insert data
INSERT INTO students (name, age, email) VALUES 
('John Doe', 20, 'john@email.com'),
('Jane Smith', 22, 'jane@email.com');

-- Query data
SELECT * FROM students;
```

## Alternative: MySQL Workbench

If VS Code connection doesn't work, you can also use **MySQL Workbench**:
1. **Open MySQL Workbench** (already installed)
2. **Click "+"** to create new connection
3. **Use same connection details**
4. **Test connection**

---
**Happy SQL practicing! 🎉**
