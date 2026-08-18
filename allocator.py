"""
Smart Room Allocation Algorithm based on Preferences and Availability
"""
from database import get_db_connection

class RoomAllocator:
    def __init__(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()
        
    def check_duplicate_allocation(self, student_id):
        self.cursor.execute('''
            SELECT COUNT(*) FROM allocations 
            WHERE student_id = ? AND status IN ('Confirmed', 'Checked-In')
        ''', (student_id,))
        return self.cursor.fetchone()[0] > 0
        
    def get_student_preferences(self, student_id):
        self.cursor.execute('''
            SELECT s.gender, p.room_type, p.floor 
            FROM students s
            LEFT JOIN preferences p ON s.id = p.student_id
            WHERE s.id = ?
        ''', (student_id,))
        return dict(self.cursor.fetchone() or {})
        
    def find_best_room(self, gender, pref_room_type, pref_floor):
        # Determine hostel type based on student gender
        hostel_type = 'Girls' if gender.lower() == 'female' else 'Boys'
        
        # Query 1: Exact match (Room Type + Floor)
        self.cursor.execute('''
            SELECT r.id, r.room_number 
            FROM rooms r
            JOIN hostels h ON r.hostel_id = h.id
            WHERE h.type = ? AND r.room_type = ? AND r.floor = ? 
            AND r.current_occupancy < r.capacity AND r.status = 'Available'
        ''', (hostel_type, pref_room_type, pref_floor))
        room = self.cursor.fetchone()
        if room:
            return room['id'], "Exact Match"
            
        # Query 2: Partial match (Room Type only)
        self.cursor.execute('''
            SELECT r.id, r.room_number 
            FROM rooms r
            JOIN hostels h ON r.hostel_id = h.id
            WHERE h.type = ? AND r.room_type = ? 
            AND r.current_occupancy < r.capacity AND r.status = 'Available'
        ''', (hostel_type, pref_room_type))
        room = self.cursor.fetchone()
        if room:
            return room['id'], "Partial Match (Room Type)"
            
        # Query 3: Any available room in the appropriate hostel
        self.cursor.execute('''
            SELECT r.id, r.room_number 
            FROM rooms r
            JOIN hostels h ON r.hostel_id = h.id
            WHERE h.type = ? 
            AND r.current_occupancy < r.capacity AND r.status = 'Available'
        ''', (hostel_type,))
        room = self.cursor.fetchone()
        if room:
            return room['id'], "Alternative Room Assigned"
            
        return None, "No Rooms Available"

    def allocate(self, student_id):
        if self.check_duplicate_allocation(student_id):
            return {"status": "error", "message": "Student already has an active allocation."}
            
        prefs = self.get_student_preferences(student_id)
        if not prefs:
            return {"status": "error", "message": "Student not found."}
            
        gender = prefs.get('gender')
        room_type = prefs.get('room_type', 'Double') # Default
        floor = prefs.get('floor', 1) # Default
        
        room_id, match_status = self.find_best_room(gender, room_type, floor)
        
        if not room_id:
            return {"status": "error", "message": "Allocation failed. Hostel is fully occupied."}
            
        # Perform allocation
        try:
            # Update room occupancy
            self.cursor.execute('''
                UPDATE rooms 
                SET current_occupancy = current_occupancy + 1,
                    status = CASE WHEN current_occupancy + 1 = capacity THEN 'Full' ELSE 'Available' END
                WHERE id = ?
            ''', (room_id,))
            
            # Create allocation record
            self.cursor.execute('''
                INSERT INTO allocations (student_id, room_id, status)
                VALUES (?, ?, 'Confirmed')
            ''', (student_id, room_id))
            
            self.conn.commit()
            
            return {
                "status": "success", 
                "room_id": room_id,
                "match_level": match_status,
                "message": "Room successfully allocated."
            }
        except Exception as e:
            self.conn.rollback()
            return {"status": "error", "message": str(e)}
