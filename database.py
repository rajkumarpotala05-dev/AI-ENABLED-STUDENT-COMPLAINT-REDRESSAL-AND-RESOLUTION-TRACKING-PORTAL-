"""
Database Setup and Connection Management for Hostel System
"""
import sqlite3
import os

DB_FILE = 'hostel.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gender TEXT NOT NULL,
        department TEXT NOT NULL,
        year INTEGER NOT NULL,
        contact TEXT NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hostels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        total_rooms INTEGER NOT NULL,
        warden_name TEXT NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostel_id INTEGER,
        room_number TEXT NOT NULL,
        room_type TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        current_occupancy INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Available',
        floor INTEGER,
        FOREIGN KEY(hostel_id) REFERENCES hostels(id)
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        room_type TEXT,
        floor INTEGER,
        amenities TEXT,
        special_needs TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        room_id INTEGER,
        allocation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        check_in DATE,
        check_out DATE,
        status TEXT DEFAULT 'Confirmed',
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(room_id) REFERENCES rooms(id)
    )''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
