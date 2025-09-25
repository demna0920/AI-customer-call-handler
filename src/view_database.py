#!/usr/bin/env python3
"""
Database Viewer for the Korean BBQ House London reservation system
"""

import sqlite3
import os
from datetime import datetime
from database import ReservationDatabase

def view_database(db_path: str = "reservations.db"):
    """View all data in the database"""
    try:
        # Check if database exists
        if not os.path.exists(db_path):
            print(f"❌ Database file '{db_path}' not found.")
            return
        
        db = ReservationDatabase(db_path)
        
        print("🍽️ Korean BBQ House London - Database Viewer")
        print("=" * 60)
        print(f"📁 Database: {db_path}")
        print()
        
        # View customers
        print("👥 Customers:")
        print("-" * 40)
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, phone, email, created_at
                    FROM customers
                    ORDER BY created_at DESC
                ''')
                customers = cursor.fetchall()
                
                if customers:
                    for customer in customers:
                        print(f"ID: {customer[0]}, Name: {customer[1]}, Phone: {customer[2]}, Email: {customer[3]}, Created: {customer[4]}")
                else:
                    print("No customers found.")
        except Exception as e:
            print(f"Error retrieving customers: {e}")
        
        print()
        
        # View reservations
        print("📅 Reservations:")
        print("-" * 40)
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT r.id, c.name, r.reservation_date, r.reservation_time, 
                           r.party_size, r.special_requests, r.created_at
                    FROM reservations r
                    JOIN customers c ON r.customer_id = c.id
                    ORDER BY r.reservation_date DESC, r.reservation_time DESC
                ''')
                reservations = cursor.fetchall()
                
                if reservations:
                    for reservation in reservations:
                        print(f"ID: {reservation[0]}, Customer: {reservation[1]}, Date: {reservation[2]}, Time: {reservation[3]}, Party: {reservation[4]}, Requests: {reservation[5]}, Created: {reservation[6]}")
                else:
                    print("No reservations found.")
        except Exception as e:
            print(f"Error retrieving reservations: {e}")
        
        print()
        
        # View today's reservations
        print("📅 Today's Reservations:")
        print("-" * 40)
        try:
            today_reservations = db.get_todays_reservations()
            if today_reservations:
                for reservation in today_reservations:
                    print(f"ID: {reservation['id']}, Customer: {reservation['customer_name']}, Time: {reservation['time']}, Party: {reservation['party_size']}, Requests: {reservation['special_requests']}")
            else:
                print("No reservations for today.")
        except Exception as e:
            print(f"Error retrieving today's reservations: {e}")
        
        print()
        print("✅ Database viewing completed!")
        
    except Exception as e:
        print(f"❌ Error viewing database: {e}")

def main():
    """Main function to run the database viewer"""
    view_database()

if __name__ == "__main__":
    main()