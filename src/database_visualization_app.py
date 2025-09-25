#!/usr/bin/env python3
"""
Simplified Flask app for database visualization only
"""

from flask import Flask, render_template_string
import sqlite3
import os
from database import ReservationDatabase
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask 앱 생성
app = Flask(__name__)

# 📊 Database Visualization Endpoint
@app.route("/database")
def database_view():
    """Display database contents in a web interface"""
    try:
        db = ReservationDatabase()
        
        # Get all customers
        with sqlite3.connect("reservations.db") as conn:
            cursor = conn.cursor()
            
            # Get customers
            cursor.execute('''
                SELECT id, name, phone, email, created_at
                FROM customers
                ORDER BY created_at DESC
            ''')
            customers = cursor.fetchall()
            
            # Get reservations
            cursor.execute('''
                SELECT r.id, c.name, r.reservation_date, r.reservation_time, 
                       r.party_size, r.special_requests, r.created_at
                FROM reservations r
                JOIN customers c ON r.customer_id = c.id
                ORDER BY r.reservation_date DESC, r.reservation_time DESC
            ''')
            reservations = cursor.fetchall()
            
            # Get today's reservations using the database method
            todays_reservations = db.get_todays_reservations()
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>📊 Reservation Database Visualization</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
                .container {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                h1, h2 {{ color: #d32f2f; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #d32f2f; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .section {{ margin: 30px 0; }}
                .back-link {{ display: inline-block; margin-bottom: 20px; color: #d32f2f; text-decoration: none; }}
                .back-link:hover {{ text-decoration: underline; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ background: #d32f2f; color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .stat-number {{ font-size: 2em; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Korean BBQ House London - Database Visualization</h1>
                
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">{len(customers)}</div>
                        <div>Total Customers</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{len(reservations)}</div>
                        <div>Total Reservations</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{len(todays_reservations)}</div>
                        <div>Today's Reservations</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>👥 Customers</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Phone</th>
                                <th>Email</th>
                                <th>Created At</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([f"<tr><td>{c[0]}</td><td>{c[1]}</td><td>{c[2] or '-'}</td><td>{c[3] or '-'}</td><td>{c[4]}</td></tr>" for c in customers])}
                        </tbody>
                    </table>
                </div>
                
                <div class="section">
                    <h2>📅 Today's Reservations</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Customer</th>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Party Size</th>
                                <th>Special Requests</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([f"<tr><td>{r['id']}</td><td>{r['customer_name']}</td><td>{r['date']}</td><td>{r['time']}</td><td>{r['party_size']}</td><td>{r['special_requests'] or '-'}</td></tr>" for r in todays_reservations]) if todays_reservations else "<tr><td colspan='6'>No reservations for today</td></tr>"}
                        </tbody>
                    </table>
                </div>
                
                <div class="section">
                    <h2>📅 All Reservations</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Customer</th>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Party Size</th>
                                <th>Special Requests</th>
                                <th>Created At</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5] or '-'}</td><td>{r[6]}</td></tr>" for r in reservations])}
                        </tbody>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        logger.error(f"Error displaying database: {e}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>❌ Database Error</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>❌ Database Visualization Error</h1>
            <p class="error">Error: {str(e)}</p>
        </body>
        </html>
        """, 500

# 🏠 Main page
@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>📞 AI Reservation System - Database Visualization</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .container { text-align: center; }
            .info-box { background: #e9f7fe; padding: 15px; border-radius: 5px; margin: 20px 0; }
            button { background: #d32f2f; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
            button:hover { background: #b71c1c; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🍖 Korean BBQ House London</h1>
            <p class="subtitle">Authentic Korean BBQ Restaurant in Central London</p>

            <div class="info-box">
                <h3>📊 Database Visualization</h3>
                <p>View all reservations and customer data:</p>
                <a href="/database" class="button">View Database</a>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True, port=5001)