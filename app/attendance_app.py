"""
Extended Attendance Application with Camera Functionality
Inherits from the base FaceRecognitionApp and adds camera-specific features
"""

import cv2
import numpy as np
import face_recognition
import threading
import time
from datetime import datetime
from .main import FaceRecognitionApp
from PIL import Image

class AttendanceApp(FaceRecognitionApp):
    """Extended Attendance App with Camera and Face Recognition"""
    
    def __init__(self, is_dev_mode=False):
        super().__init__(is_dev_mode)
        self.setup_attendance_features()
    
    def setup_attendance_features(self):
        """Setup attendance-specific features"""
        # Attendance tracking
        self.last_detection_time = {}  # Track last detection per student
        self.detection_cooldown = 3  # 3 seconds between detections
        
        # Camera frame processing
        self.frame_skip = 0
        self.max_frame_skip = 2  # Process every 3rd frame for performance
        
        print("✅ Attendance features initialized")
    
    def update_frame(self):
        """Update camera frame with face recognition"""
        while self.running and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                # Skip frames for performance
                self.frame_skip += 1
                if self.frame_skip < self.max_frame_skip:
                    continue
                self.frame_skip = 0
                
                # Resize frame for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Find faces in frame
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                # Process each face found
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # Scale back to original size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    
                    # Check if face matches known students
                    matches = face_recognition.compare_faces(self.encode_list_known, face_encoding, tolerance=0.6)
                    face_distance = face_recognition.face_distance(self.encode_list_known, face_encoding)
                    
                    if True in matches:
                        best_match_index = np.argmin(face_distance)
                        if matches[best_match_index]:
                            name = self.student_names[best_match_index]
                            self.process_student_detection(name, frame, (top, right, bottom, left))
                    else:
                        self.process_unknown_face(frame, (top, right, bottom, left))
                
                # Update camera panel
                self.update_camera_display(frame)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"❌ Frame processing error: {e}")
                time.sleep(0.1)
    
    def process_student_detection(self, name, frame, bbox):
        """Process detected student face"""
        top, right, bottom, left = bbox
        current_time = time.time()
        
        # Check cooldown
        if name in self.last_detection_time:
            if current_time - self.last_detection_time[name] < self.detection_cooldown:
                return
        
        # Update last detection time
        self.last_detection_time[name] = current_time
        
        # Mark attendance
        if self.mark_attendance(name):
            # Add to present students
            self.present_students.add(name)
            
            # Update student card
            self.students_panel.update_student_card(name, True)
            
            # Update stats
            self.control_panel.update_stats(
                total_students=len(self.student_data),
                marked_present=len(self.present_students),
                unknown_detected=self.unknown_count
            )
            
            print(f"✅ Student detected: {name}")
        
        # Draw bounding box
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    def process_unknown_face(self, frame, bbox):
        """Process unknown face detection"""
        top, right, bottom, left = bbox
        current_time = time.time()
        
        # Check cooldown for unknown faces
        if 'unknown' in self.last_detection_time:
            if current_time - self.last_detection_time['unknown'] < self.detection_cooldown:
                return
        
        # Update last detection time
        self.last_detection_time['unknown'] = current_time
        
        # Increment unknown count
        self.unknown_count += 1
        
        # Update stats
        self.control_panel.update_stats(
            total_students=len(self.student_data),
            marked_present=len(self.present_students),
            unknown_detected=self.unknown_count
        )
        
        # Draw bounding box for unknown face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, "UNKNOWN", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        print(f"❓ Unknown face detected (total: {self.unknown_count})")
    
    def update_camera_display(self, frame):
        """Update camera panel display"""
        try:
            # Convert frame to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Update camera panel
            self.camera_panel.update_frame(pil_image)
            
        except Exception as e:
            print(f"❌ Camera display update error: {e}")
    
    def start_camera(self):
        """Start camera with attendance features"""
        super().start_camera()
        
        if self.camera_initialized:
            # Initialize camera panel
            self.camera_panel.camera_ready()
            
            # Update control panel
            self.control_panel.camera_ready()
            
            print("✅ Attendance camera started")
    
    def stop_camera(self):
        """Stop camera and cleanup attendance features"""
        super().stop_camera()
        
        # Reset attendance state
        self.present_students.clear()
        self.unknown_count = 0
        self.last_detection_time.clear()
        
        # Update UI
        self.students_panel.clear_all_cards()
        self.control_panel.reset_state()
        
        print("✅ Attendance camera stopped")
    
    def get_attendance_summary(self):
        """Get current attendance summary"""
        return {
            'total_students': len(self.student_data),
            'present': len(self.present_students),
            'absent': len(self.student_data) - len(self.present_students),
            'unknown_detected': self.unknown_count,
            'present_students': list(self.present_students)
        }
    
    def export_attendance(self, filename=None):
        """Export attendance data"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"attendance_export_{timestamp}.csv"
        
        try:
            import pandas as pd
            
            # Read current attendance
            df = pd.read_csv(self.attendance_path)
            
            # Add summary
            summary = self.get_attendance_summary()
            summary_df = pd.DataFrame([summary])
            
            # Export
            export_path = self.project_root / filename
            with open(export_path, 'w') as f:
                f.write("=== ATTENDANCE SUMMARY ===\n")
                summary_df.to_csv(f, index=False)
                f.write("\n=== DETAILED ATTENDANCE ===\n")
                df.to_csv(f, index=False)
            
            print(f"✅ Attendance exported to: {export_path}")
            return str(export_path)
            
        except ImportError:
            print("❌ pandas not available for export")
            return None
        except Exception as e:
            print(f"❌ Export error: {e}")
            return None

# Factory functions
def create_attendance_app(is_dev_mode=False):
    """Create attendance app instance"""
    return AttendanceApp(is_dev_mode=is_dev_mode)

if __name__ == "__main__":
    # Test the attendance app
    app = AttendanceApp()
    app.run()
