"""
Attendance Service
Handles attendance-related business logic and API operations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from ..database.connection import get_db
import logging

class AttendanceService:
    """Service for managing attendance operations"""
    
    def __init__(self):
        self.db = get_db()
        self.logger = logging.getLogger(__name__)
    
    def mark_attendance(self, student_id: int, timestamp: datetime = None) -> bool:
        """Mark student attendance"""
        if not timestamp:
            timestamp = datetime.now()
        
        query = """
            INSERT INTO attendance (student_id, timestamp, created_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            timestamp = VALUES(timestamp),
            updated_at = VALUES(created_at)
        """
        
        try:
            attendance_id = self.db.insert(query, (student_id, timestamp, timestamp))
            if attendance_id:
                self.logger.info(f"✅ Attendance marked for student {student_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Error marking attendance: {e}")
            return False
    
    def get_attendance_by_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Get attendance records for a specific date"""
        query = """
            SELECT 
                a.id,
                s.name as student_name,
                s.student_id as student_code,
                a.timestamp,
                a.created_at
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE DATE(a.timestamp) = %s
            ORDER BY a.timestamp ASC
        """
        
        try:
            results = self.db.fetch_all(query, (target_date,))
            return [
                {
                    'id': row[0],
                    'student_name': row[1],
                    'student_code': row[2],
                    'timestamp': row[3],
                    'created_at': row[4]
                }
                for row in results
            ]
        except Exception as e:
            self.logger.error(f"❌ Error fetching attendance: {e}")
            return []
    
    def get_attendance_summary(self, target_date: date = None) -> Dict[str, Any]:
        """Get attendance summary for a date"""
        if not target_date:
            target_date = date.today()
        
        # Get total students
        total_query = "SELECT COUNT(*) FROM students WHERE status = 'active'"
        total_students = self.db.fetch_one(total_query, ())[0] if self.db.fetch_one(total_query, ()) else 0
        
        # Get present students
        present_query = """
            SELECT COUNT(DISTINCT student_id) 
            FROM attendance 
            WHERE DATE(timestamp) = %s
        """
        present_count = self.db.fetch_one(present_query, (target_date,))[0] if self.db.fetch_one(present_query, (target_date,)) else 0
        
        return {
            'date': target_date,
            'total_students': total_students,
            'present': present_count,
            'absent': total_students - present_count,
            'attendance_rate': round((present_count / total_students * 100), 2) if total_students > 0 else 0
        }
    
    def get_student_attendance_history(self, student_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get attendance history for a specific student"""
        query = """
            SELECT 
                DATE(timestamp) as date,
                timestamp,
                created_at
            FROM attendance
            WHERE student_id = %s
            AND timestamp >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            ORDER BY timestamp DESC
        """
        
        try:
            results = self.db.fetch_all(query, (student_id, days))
            return [
                {
                    'date': row[0],
                    'timestamp': row[1],
                    'created_at': row[2]
                }
                for row in results
            ]
        except Exception as e:
            self.logger.error(f"❌ Error fetching student history: {e}")
            return []
    
    def export_attendance_report(self, start_date: date, end_date: date, format: str = 'csv') -> Optional[str]:
        """Export attendance report for date range"""
        query = """
            SELECT 
                s.name as student_name,
                s.student_id as student_code,
                DATE(a.timestamp) as date,
                TIME(a.timestamp) as time,
                a.created_at
            FROM students s
            LEFT JOIN attendance a ON s.id = a.student_id 
                AND DATE(a.timestamp) BETWEEN %s AND %s
            WHERE s.status = 'active'
            ORDER BY s.name, a.timestamp
        """
        
        try:
            results = self.db.fetch_all(query, (start_date, end_date))
            
            if format.lower() == 'csv':
                return self._export_to_csv(results, start_date, end_date)
            else:
                self.logger.warning(f"⚠️  Unsupported format: {format}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error exporting report: {e}")
            return None
    
    def _export_to_csv(self, results: List[tuple], start_date: date, end_date: date) -> str:
        """Export results to CSV format"""
        try:
            from pathlib import Path
            import csv
            
            # Create export directory
            export_dir = Path(__file__).parent.parent.parent / "exports"
            export_dir.mkdir(exist_ok=True)
            
            # Generate filename
            filename = f"attendance_report_{start_date}_{end_date}.csv"
            filepath = export_dir / filename
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Student Name', 'Student Code', 'Date', 'Time', 'Created At'])
                
                # Write data
                for row in results:
                    writer.writerow(row)
            
            self.logger.info(f"✅ Report exported to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"❌ CSV export error: {e}")
            return None

# Global service instance
attendance_service = AttendanceService()

def get_attendance_service() -> AttendanceService:
    """Get attendance service instance"""
    return attendance_service
