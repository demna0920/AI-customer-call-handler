# Database Visualization Guide

This guide explains how to use the database visualization feature for the Korean BBQ House London reservation system.

## Overview

The database visualization feature provides a web-based interface to view all customer and reservation data stored in the SQLite database. This allows restaurant staff to easily monitor reservations, track customer information, and view today's bookings.

## Prerequisites

- Python 3.8 or higher
- Flask web framework
- SQLite database with reservation data

## Running the Database Visualization

1. Make sure you're in the project directory:
   ```bash
   cd /path/to/reservation-system
   ```

2. Activate the virtual environment:
   ```bash
   source reservation_env/bin/activate
   ```

3. Run the database visualization app:
   ```bash
   python database_visualization_app.py
   ```

4. Open your web browser and navigate to:
   ```
   http://localhost:5001
   ```

5. Click on the "View Database" button to access the database visualization page:
   ```
   http://localhost:5001/database
   ```

## Features

The database visualization page includes:

### Statistics Overview
- Total number of customers
- Total number of reservations
- Number of reservations for today

### Customer Data
- List of all customers with their:
  - ID
  - Name
  - Phone number
  - Email address
  - Account creation date

### Today's Reservations
- List of all reservations scheduled for today with:
  - Reservation ID
  - Customer name
  - Reservation date
  - Reservation time
  - Party size
  - Special requests

### All Reservations
- Complete list of all reservations in the system, sorted by date and time:
  - Reservation ID
  - Customer name
  - Reservation date
  - Reservation time
  - Party size
  - Special requests
  - Creation timestamp

## Data Structure

The system uses two main database tables:

### Customers Table
- `id`: Unique customer identifier
- `name`: Customer's name
- `phone`: Customer's phone number (optional)
- `email`: Customer's email address (optional)
- `created_at`: Timestamp when the customer record was created

### Reservations Table
- `id`: Unique reservation identifier
- `customer_id`: Foreign key referencing the customer
- `reservation_date`: Date of the reservation (YYYY-MM-DD)
- `reservation_time`: Time of the reservation (HH:MM)
- `party_size`: Number of people in the party (default: 2)
- `special_requests`: Any special requests from the customer
- `created_at`: Timestamp when the reservation was created

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Make sure you've activated the virtual environment before running the app
   - Install required dependencies with: `pip install flask`

2. **Database connection errors**
   - Ensure the `reservations.db` file exists in the project directory
   - Check that the database file has proper read permissions

3. **Port already in use**
   - The app uses port 5001 by default
   - Change the port by modifying the `app.run()` line in `database_visualization_app.py`

### Viewing Raw Database Data

If you need to view the raw database contents, you can use the provided `view_database.py` script:
```bash
python view_database.py
```

Or access the SQLite database directly:
```bash
sqlite3 reservations.db
.tables
SELECT * FROM customers;
SELECT * FROM reservations;
```

## Customization

You can customize the database visualization by modifying the `database_visualization_app.py` file:

1. **Change the port**:
   ```python
   if __name__ == "__main__":
       app.run(debug=True, port=5002)  # Change to your preferred port
   ```

2. **Modify the styling**:
   - Edit the CSS styles in the HTML template strings
   - Change colors, fonts, and layout as needed

3. **Add new data views**:
   - Extend the database queries to include additional information
   - Add new sections to the HTML template

## Security Considerations

When deploying this visualization in a production environment, consider:

1. **Authentication**: Add user authentication to restrict access
2. **HTTPS**: Use HTTPS to encrypt data transmission
3. **Input validation**: Validate all user inputs
4. **Rate limiting**: Implement rate limiting to prevent abuse
5. **Database permissions**: Ensure the database file has appropriate permissions

## Support

For issues with the database visualization feature, please contact the development team or check the project documentation.