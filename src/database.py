#!/usr/bin/env python3
"""
Database module for the Korean BBQ House London reservation system
"""

import sqlite3
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReservationDatabase:
    """Handles database operations for reservations and customers"""
    
    def __init__(self, db_path: str = None):
        """Initialize the database connection and create tables if they don't exist"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "reservations.db")
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create customers table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT,
                        email TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create reservations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reservations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id INTEGER,
                        reservation_date DATE NOT NULL,
                        reservation_time TIME NOT NULL,
                        party_size INTEGER DEFAULT 2,
                        special_requests TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES customers (id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_reservations_date 
                    ON reservations (reservation_date)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_reservations_customer 
                    ON reservations (customer_id)
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def create_customer(self, name: str, phone: str = None, email: str = None) -> int:
        """
        Create a new customer record
        
        Args:
            name (str): Customer name
            phone (str, optional): Customer phone number
            email (str, optional): Customer email
            
        Returns:
            int: Customer ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO customers (name, phone, email)
                    VALUES (?, ?, ?)
                ''', (name, phone, email))
                conn.commit()
                customer_id = cursor.lastrowid
                logger.info(f"Created customer: {name} with ID {customer_id}")
                return customer_id
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            raise
    
    def update_customer(self, customer_id: int, **kwargs) -> bool:
        """
        Update customer information
        
        Args:
            customer_id (int): Customer ID
            **kwargs: Fields to update (phone, email)
            
        Returns:
            bool: True if updated, False if not found
        """
        try:
            if not kwargs:
                return False
                
            # Build dynamic update query
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in ['phone', 'email']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
                
            values.append(customer_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    UPDATE customers
                    SET {', '.join(fields)}
                    WHERE id = ?
                ''', values)
                conn.commit()
                updated = cursor.rowcount > 0
                if updated:
                    logger.info(f"Updated customer ID {customer_id}")
                return updated
        except Exception as e:
            logger.error(f"Error updating customer: {e}")
            raise
    
    def get_customer_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get customer by name
        
        Args:
            name (str): Customer name
            
        Returns:
            dict: Customer information or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, phone, email, created_at
                    FROM customers
                    WHERE name = ?
                ''', (name,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'name': row[1],
                        'phone': row[2],
                        'email': row[3],
                        'created_at': row[4]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting customer: {e}")
            raise
    
    def create_reservation(self, customer_id: int, reservation_date: str, 
                          reservation_time: str, party_size: int = 2, 
                          special_requests: str = None) -> int:
        """
        Create a new reservation
        
        Args:
            customer_id (int): Customer ID
            reservation_date (str): Reservation date (YYYY-MM-DD)
            reservation_time (str): Reservation time (HH:MM)
            party_size (int): Number of people in the party
            special_requests (str): Special requests
            
        Returns:
            int: Reservation ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO reservations 
                    (customer_id, reservation_date, reservation_time, party_size, special_requests)
                    VALUES (?, ?, ?, ?, ?)
                ''', (customer_id, reservation_date, reservation_time, party_size, special_requests))
                conn.commit()
                reservation_id = cursor.lastrowid
                logger.info(f"Created reservation ID {reservation_id} for customer {customer_id}")
                return reservation_id
        except Exception as e:
            logger.error(f"Error creating reservation: {e}")
            raise
    def check_duplicate_reservation(self, name: str, date: str, time: str) -> bool:
        """
        Check if a reservation already exists for the given name, date, and time
        
        Args:
            name (str): Customer name
            date (str): Reservation date (YYYY-MM-DD)
            time (str): Reservation time (HH:MM)
            
        Returns:
            bool: True if duplicate exists, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*)
                    FROM reservations r
                    JOIN customers c ON r.customer_id = c.id
                    WHERE c.name = ? AND r.reservation_date = ? AND r.reservation_time = ?
                ''', (name, date, time))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"Error checking duplicate reservation: {e}")
            return False
    def get_todays_reservations(self) -> list:
        """
        Get all reservations for today
        
        Returns:
            list: List of today's reservations
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT r.id, c.name, r.reservation_date, r.reservation_time, 
                           r.party_size, r.special_requests
                    FROM reservations r
                    JOIN customers c ON r.customer_id = c.id
                    WHERE r.reservation_date = ?
                    ORDER BY r.reservation_time
                ''', (today,))
                rows = cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'customer_name': row[1],
                        'date': row[2],
                        'time': row[3],
                        'party_size': row[4],
                        'special_requests': row[5]
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error getting today's reservations: {e}")
            raise
    
    def get_reservation_by_id(self, reservation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get reservation by ID
        
        Args:
            reservation_id (int): Reservation ID
            
        Returns:
            dict: Reservation information or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT r.id, c.name, r.reservation_date, r.reservation_time, 
                           r.party_size, r.special_requests, r.created_at
                    FROM reservations r
                    JOIN customers c ON r.customer_id = c.id
                    WHERE r.id = ?
                ''', (reservation_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'customer_name': row[1],
                        'date': row[2],
                        'time': row[3],
                        'party_size': row[4],
                        'special_requests': row[5],
                        'created_at': row[6]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting reservation: {e}")
            raise
    
    def update_reservation(self, reservation_id: int, **kwargs) -> bool:
        """
        Update reservation details
        
        Args:
            reservation_id (int): Reservation ID
            **kwargs: Fields to update
            
        Returns:
            bool: True if updated, False if not found
        """
        try:
            if not kwargs:
                return False
                
            # Build dynamic update query
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in ['reservation_date', 'reservation_time', 'party_size', 'special_requests']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
                
            values.append(reservation_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    UPDATE reservations
                    SET {', '.join(fields)}
                    WHERE id = ?
                ''', values)
                conn.commit()
                updated = cursor.rowcount > 0
                if updated:
                    logger.info(f"Updated reservation ID {reservation_id}")
                return updated
        except Exception as e:
            logger.error(f"Error updating reservation: {e}")
            raise

# Global database instance
db = ReservationDatabase()

if __name__ == "__main__":
    # Test the database
    print("Testing database...")
    try:
        # Create a test customer
        customer_id = db.create_customer("Test Customer", "07700 900123", "test@example.com")
        print(f"Created customer with ID: {customer_id}")
        
        # Create a test reservation
        reservation_id = db.create_reservation(
            customer_id, 
            "2025-09-05", 
            "19:00", 
            4, 
            "Window seat preferred"
        )
        print(f"Created reservation with ID: {reservation_id}")
        
        # Get the reservation
        reservation = db.get_reservation_by_id(reservation_id)
        print(f"Retrieved reservation: {reservation}")
        
        print("Database test completed successfully!")
    except Exception as e:
        print(f"Database test failed: {e}")