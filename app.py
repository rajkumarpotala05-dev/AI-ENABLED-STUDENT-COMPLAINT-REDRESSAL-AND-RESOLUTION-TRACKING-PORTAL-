"""
Smart Hostel Room Allocation and Occupancy Management System
Main Application Entry Point
"""
from flask import Flask, render_template, request, jsonify
from database import init_db, get_db_connection
from allocator import RoomAllocator
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return jsonify({"status": "Smart Hostel Management API is running."})

@app.route('/api/students', methods=['GET', 'POST'])
def manage_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = request.json
        cursor.execute("INSERT INTO students (name, gender, department, year, contact) VALUES (?, ?, ?, ?, ?)",
                       (data['name'], data['gender'], data['department'], data['year'], data['contact']))
        conn.commit()
        return jsonify({"status": "success", "student_id": cursor.lastrowid})
    
    cursor.execute("SELECT * FROM students")
    students = [dict(row) for row in cursor.fetchall()]
    return jsonify(students)

@app.route('/api/preferences', methods=['POST'])
def submit_preferences():
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.json
    cursor.execute("INSERT INTO preferences (student_id, room_type, floor, amenities, special_needs) VALUES (?, ?, ?, ?, ?)",
                   (data['student_id'], data['room_type'], data['floor'], data['amenities'], data.get('special_needs', '')))
    conn.commit()
    return jsonify({"status": "success", "pref_id": cursor.lastrowid})

@app.route('/api/rooms', methods=['GET', 'POST'])
def manage_rooms():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = request.json
        cursor.execute("INSERT INTO rooms (hostel_id, room_number, room_type, capacity, current_occupancy, status) VALUES (?, ?, ?, ?, 0, 'Available')",
                       (data['hostel_id'], data['room_number'], data['room_type'], data['capacity']))
        conn.commit()
        return jsonify({"status": "success", "room_id": cursor.lastrowid})
    
    cursor.execute("SELECT * FROM rooms")
    rooms = [dict(row) for row in cursor.fetchall()]
    return jsonify(rooms)

@app.route('/api/allocate', methods=['POST'])
def allocate_room():
    data = request.json
    student_id = data.get('student_id')
    
    allocator = RoomAllocator()
    result = allocator.allocate(student_id)
    
    return jsonify(result)

@app.route('/api/occupancy/<hostel_id>', methods=['GET'])
def get_occupancy(hostel_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.room_number, r.room_type, r.capacity, r.current_occupancy, r.status
        FROM rooms r
        WHERE r.hostel_id = ?
        ORDER BY r.room_number
    ''', (hostel_id,))
    
    occupancy = [dict(row) for row in cursor.fetchall()]
    return jsonify(occupancy)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
