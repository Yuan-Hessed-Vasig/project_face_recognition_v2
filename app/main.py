"""
Main Application Module for Face Recognition Attendance App
This serves as the base app shell that can be imported by attendance.py and dev.py
"""

import os
import cv2
import numpy as np
import face_recognition
import customtkinter as ctk
from PIL import Image, ImageTk
from datetime import datetime
import threading
import pywinstyles
import random
import json
import signal
import sys
from pathlib import Path

class FaceRecognitionApp:
    """Base Face Recognition Application Class"""
    
    def __init__(self, is_dev_mode=False):
        self.is_dev_mode = is_dev_mode
        self.setup_paths()
        self.load_student_data()
        self.prepare_attendance_file()
        self.load_face_encodings()
        
        # Initialize GUI components
        self.setup_gui()
        
        # Development mode indicators
        if self.is_dev_mode:
            self.setup_dev_mode()
    
    def setup_paths(self):
        """Setup all necessary file paths"""
        # Get the app directory (this file's location)
        self.app_dir = Path(__file__).parent.absolute()
        self.project_root = self.app_dir.parent
        
        # Define all paths relative to app directory
        self.students_dir = self.app_dir / "Images" / "Students"
        self.attendance_path = self.app_dir / "attendance.csv"
        self.bg_image_path = self.app_dir / "Images" / "Background" / "cube.jpg"
        self.students_json_path = self.students_dir / "students.json"
        
        print(f"📁 App Directory: {self.app_dir}")
        print(f"📁 Project Root: {self.project_root}")
    
    def load_student_data(self):
        """Load student data from JSON file"""
        try:
            if self.students_json_path.exists():
                with open(self.students_json_path, 'r') as f:
                    self.student_data = {student['name']: student for student in json.load(f)}
                print(f"✅ Loaded {len(self.student_data)} students from JSON")
            else:
                self.student_data = {}
                print("⚠️  No students.json found, using empty student data")
        except Exception as e:
            print(f"❌ Error loading student data: {e}")
            self.student_data = {}
    
    def prepare_attendance_file(self):
        """Prepare attendance CSV file"""
        if not self.students_dir.exists():
            raise FileNotFoundError(f"Student images folder not found: {self.students_dir}")
        
        if not self.attendance_path.exists():
            with open(self.attendance_path, "w") as f:
                f.write("Name,Timestamp\n")
            print(f"✅ Created attendance file: {self.attendance_path}")
    
    def load_face_encodings(self):
        """Load and encode student faces"""
        self.encode_list_known = []
        self.student_names = []
        
        if not self.students_dir.exists():
            print("⚠️  Students directory not found")
            return
        
        for student in os.listdir(self.students_dir):
            folder = self.students_dir / student
            if not folder.is_dir():
                continue
                
            for file in os.listdir(folder):
                path = folder / file
                img = cv2.imread(str(path))
                if img is None:
                    continue
                    
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encs = face_recognition.face_encodings(rgb)
                if encs:
                    self.encode_list_known.append(encs[0])
                    self.student_names.append(student.upper())
        
        print(f"✅ Loaded {len(self.encode_list_known)} encodings for {len(set(self.student_names))} students")
    
    def mark_attendance(self, name):
        """Mark student attendance"""
        try:
            with open(self.attendance_path, "r+", newline="") as f:
                entries = f.readlines()
                names = [e.split(',')[0] for e in entries]
                if name not in names:
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"{name},{now}\n")
                    print(f"✅ Marked {name} at {now}")
                    return True
                else:
                    print(f"⚠️  {name} already marked today")
                    return False
        except Exception as e:
            print(f"❌ Error marking attendance: {e}")
            return False
    
    def setup_gui(self):
        """Setup the main GUI window"""
        self.root = ctk.CTk()
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("1200x800")
        
        # Apply modern styling
        try:
            pywinstyles.apply_style(self.root, "dark")
        except:
            pass  # Fallback if pywinstyles fails
        
        # Initialize GUI state
        self.running = False
        self.camera_initialized = False
        self.cap = None
        self.present_students = set()
        self.unknown_count = 0
        self.color_index = 0
        
        # Setup GUI layout first (components need main_content)
        self.setup_layout()
        # Setup GUI components
        self.setup_components()
        # Place components in the layout
        self.place_components()
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def setup_components(self):
        """Setup GUI components"""
        # Import components here to avoid circular imports
        from .components.control_panel import ControlPanel
        from .components.students_panel import StudentsPanel
        from .components.camera_panel import CameraPanel
        from .components.loading_window import LoadingWindow
        from .components.confirm_dialog import ConfirmDialog
        
        # Initialize components
        self.control_panel = ControlPanel(self)
        self.students_panel = StudentsPanel(self)
        self.camera_panel = CameraPanel(self)
        self.loading_window = None
        self.confirm_dialog = None
    
    def setup_layout(self):
        """Setup the main layout"""
        # Create main_content attribute that components expect
        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid layout
        self.main_content.grid_columnconfigure(0, weight=0, minsize=300)  # Control Panel
        self.main_content.grid_columnconfigure(1, weight=1)               # Camera Panel
        self.main_content.grid_columnconfigure(2, weight=0, minsize=300)  # Students Panel
        self.main_content.grid_rowconfigure(0, weight=1)
    
    def place_components(self):
        """Place components in the grid layout (called after components are created)"""
        # Place components in grid
        self.control_panel.container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.camera_panel.container.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.students_panel.container.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
    
    def setup_dev_mode(self):
        """Setup development mode features"""
        if self.is_dev_mode:
            # Add dev mode indicator
            dev_label = ctk.CTkLabel(
                self.root, 
                text="🔥 DEV MODE - Hot Reload Active", 
                text_color="orange",
                font=("Arial", 12, "bold")
            )
            dev_label.pack(side="top", pady=5)
            
            print("🔥 Development mode activated with hot reload")
    
    def start_camera(self):
        """Start the camera feed"""
        if self.running:
            print("⚠️  Camera is already running")
            return
        
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Failed to open camera")
            
            self.camera_initialized = True
            self.running = True
            
            # Start camera thread
            threading.Thread(target=self.update_frame, daemon=True).start()
            print("✅ Camera started successfully")
            
        except Exception as e:
            print(f"❌ Failed to start camera: {e}")
            self.camera_initialized = False
    
    def stop_camera(self):
        """Stop the camera feed"""
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.camera_initialized = False
        print("✅ Camera stopped")
    
    def update_frame(self):
        """Update camera frame (to be implemented by subclasses)"""
        pass
    
    # Methods that components expect
    def toggle_camera(self):
        """Toggle camera on/off"""
        if self.running:
            self.stop_camera()
        else:
            self.start_camera()
    
    def close_camera(self):
        """Close camera completely"""
        self.stop_camera()
    
    def minimize_window(self):
        """Minimize the window"""
        self.root.iconify()
    
    def toggle_maximize(self):
        """Toggle maximize/restore window"""
        if self.root.state() == 'zoomed':
            self.root.state('normal')
        else:
            self.root.state('zoomed')
    
    def close_window(self):
        """Close the window"""
        self.on_closing()
    
    def run(self):
        """Run the application"""
        try:
            print("🚀 Starting Face Recognition Attendance App...")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n🛑 Received keyboard interrupt")
        except Exception as e:
            print(f"❌ Application error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")
        self.stop_camera()
        if hasattr(self, 'root') and self.root:
            self.root.quit()
        print("✅ Cleanup complete")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}")
        self.cleanup()
        sys.exit(0)
    
    def on_closing(self):
        """Handle window closing"""
        print("🔄 Closing application...")
        self.cleanup()

# Development mode helper
def create_dev_app():
    """Create app instance in development mode"""
    return FaceRecognitionApp(is_dev_mode=True)

# Production mode helper
def create_prod_app():
    """Create app instance in production mode"""
    return FaceRecognitionApp(is_dev_mode=False)

if __name__ == "__main__":
    # This allows the app to be run directly for testing
    app = FaceRecognitionApp()
    app.run()
