# Database Query Guide

This guide explains how to view and query the reservation system database.

## Using the View Database Script

The easiest way to view the database contents is to use the provided `view_database.py` script:

```bash
python view_database.py
```

This script will display:
1. All customers in the database
2. All reservations in the database
3. Today's reservations

## Direct SQLite Queries

If you prefer to query the database directly using SQLite commands, here are some useful queries:

### View All Customers
```sql
SELECT * FROM customers;
```

### View All Reservations
```sql
SELECT r.id, c.name, r.reservation_date, r.reservation_time, r.party_size, r.special_requests
FROM reservations r
JOIN customers c ON r.customer_id = c.id;
```

### View Today's Reservations
```sql
SELECT r.id, c.name, r.reservation_date, r.reservation_time, r.party_size, r.special_requests
FROM reservations r
JOIN customers c ON r.customer_id = c.id
WHERE r.reservation_date = date('now');
```

### View Reservations for a Specific Date
```sql
SELECT r.id, c.name, r.reservation_date, r.reservation_time, r.party_size, r.special_requests
FROM reservations r
JOIN customers c ON r.customer_id = c.id
WHERE r.reservation_date = '2025-09-05';  -- Replace with desired date
```

### View Reservations for a Specific Customer
```sql
SELECT r.id, c.name, r.reservation_date, r.reservation_time, r.party_size, r.special_requests
FROM reservations r
JOIN customers c ON r.customer_id = c.id
WHERE c.name LIKE '%James%';  -- Replace with customer name
```

## Database Schema

### Customers Table
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Reservations Table
```sql
CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    reservation_date DATE NOT NULL,
    reservation_time TIME NOT NULL,
    party_size INTEGER DEFAULT 2,
    special_requests TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);
```

## Using SQLite Command Line

To access the database directly using SQLite command line:

1. Install SQLite if not already installed
2. Navigate to the project directory
3. Run: `sqlite3 reservations.db`
4. Execute queries as shown above
5. Type `.exit` to quit

Example:
```bash
sqlite3 reservations.db
.tables
SELECT * FROM customers;
.exit