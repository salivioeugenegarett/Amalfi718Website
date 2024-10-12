# database.py
import sqlite3

# Initialize the database connection
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Define the Booking model
class Booking:
    def __init__(self, check_in, check_in_time, check_out, check_out_time, room, adults, children, requests):
        self.check_in = check_in
        self.check_in_time = check_in_time
        self.check_out = check_out
        self.check_out_time = check_out_time
        self.room = room
        self.adults = adults
        self.children = children
        self.requests = requests

    # Save booking to database
    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bookings (check_in, check_in_time, check_out, check_out_time, room, adults, children, requests) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
            (self.check_in, self.check_in_time, self.check_out, self.check_out_time, self.room, self.adults, self.children, self.requests))
        conn.commit()
        conn.close()
