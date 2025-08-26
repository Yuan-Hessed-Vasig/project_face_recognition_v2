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
# Robustly locate the app/ directory (works whether script run from different CWD)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Candidate locations to check for the 'app' folder
candidates = [
    os.path.join(os.path.dirname(script_dir), "app"),  # parent_of_project/ app
    os.path.join(script_dir, "app"),                   # project/app (if script in root)
]

# also walk up a few levels and check sibling 'app'
p = script_dir
for _ in range(4):
    parent = os.path.dirname(p)
    if not parent or parent == p:
        break
    candidates.append(os.path.join(parent, "app"))
    p = parent

app_dir = None
for c in candidates:
    if os.path.isdir(c):
        app_dir = c
        break

if not app_dir:
    print("Tried app folder candidates:", candidates, file=sys.stderr)
    raise FileNotFoundError(f"App folder not found. Checked candidates (see stderr).")

students_dir = os.path.join(app_dir, "Images", "Students")
attendance_path = os.path.join(app_dir, "attendance.csv")
bg_image_path = os.path.join(app_dir, "Images", "Background", "cube.jpg")
students_json_path = os.path.join(students_dir, "students.json")

# Load student data from JSON
def load_student_data():
    try:
        with open(students_json_path, 'r') as f:
            return {student['name']: student for student in json.load(f)}
    except Exception as e:
        print(f"Error loading student data: {e}")
        return {}

# Global student data
STUDENT_DATA = load_student_data()

# Prepare attendance file
if not os.path.isdir(students_dir):
    raise FileNotFoundError(f"Student images folder not found: {students_dir}")
if not os.path.isfile(attendance_path):
    with open(attendance_path, "w") as f:
        f.write("Name,Timestamp\n")

# Load and encode student faces
encodeListKnown = []
studentNames = []
for student in os.listdir(students_dir):
    folder = os.path.join(students_dir, student)
    if not os.path.isdir(folder): continue
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        img = cv2.imread(path)
        if img is None: continue
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encs = face_recognition.face_encodings(rgb)
        if encs:
            encodeListKnown.append(encs[0])
            studentNames.append(student.upper())
print(f"Loaded {len(encodeListKnown)} encodings for {len(set(studentNames))} students.")

# Attendance function
def markAttendance(name):
    with open(attendance_path, "r+", newline="") as f:
        entries = f.readlines()
        names = [e.split(',')[0] for e in entries]
        if name not in names:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{name},{now}\n")
            print(f"Marked {name} at {now}")

# GUI Application
class LoadingScreen(ctk.CTkToplevel):
    def __init__(self, parent, message="Loading..."):
        super().__init__(parent)
        self.title("")
        
        # Calculate center position
        window_width = 300
        window_height = 150
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        # Set window properties
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create loading frame
        self.loading_frame = ctk.CTkFrame(self, corner_radius=10)
        self.loading_frame.grid(row=0, column=0, padx=10, pady=20, sticky="nsew")
        
        # Add loading message
        self.loading_label = ctk.CTkLabel(self.loading_frame, 
                                        text=message,
                                        font=("Arial Bold", 14))
        self.loading_label.pack(pady=20)
        
        # Add progress bar
        self.progress_bar = ctk.CTkProgressBar(self.loading_frame)
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.start()

def get_student_image(name):
    """Get the first available image from student's folder"""
    student_folder = os.path.join(students_dir, name)
    if os.path.exists(student_folder):
        for file in os.listdir(student_folder):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                return os.path.join(student_folder, file)
    return None

# GUI Application
class AttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Face Recognition Attendance")
        
        # Remove default window decorations
        self.overrideredirect(True)
        
        # Set window to fullscreen
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        pywinstyles.apply_style(self, style="mica")
        # Remove topmost attribute so dialogs can show above
        self.attributes('-topmost', False)

        # Initialize variables
        self.initialize_variables()
        
        # Setup background
        self.setup_background()
        
        # Create main content frame
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Calculate fixed widths for side panels (15% each)
        side_panel_width = int(self.screen_width * 0.15)  # 15% of screen width
        
        # Configure grid weights for size distribution (15% - 70% - 15%)
        self.main_content.grid_columnconfigure(0, weight=0, minsize=side_panel_width)  # Control Panel fixed 15%
        self.main_content.grid_columnconfigure(1, weight=1)  # Camera Panel takes remaining space
        self.main_content.grid_columnconfigure(2, weight=0, minsize=side_panel_width)  # Students Panel fixed 15%
        self.main_content.grid_rowconfigure(0, weight=1)

        # Initialize panels using our component classes
        self.control_panel = ControlPanel(self)
        self.camera_panel = CameraPanel(self)
        self.students_panel = StudentsPanel(self)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.cap = None
        self.running = False
        self.camera_initialized = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def initialize_variables(self):
        self.unknown_count = 0
        self.present_students = set()
        self.face_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        self.color_index = 0
        self.detected_faces = {}
        self.student_ids = {}
        # Track unknown faces to prevent multiple detections
        self.unknown_faces = set()  # Store face encodings of unknown people
        # Frame processing variables
        self.skip_frames = 0  # Counter for frame skipping
        self.PROCESS_EVERY_N_FRAMES = 3  # Only process every Nth frame
        self.UNKNOWN_FACE_THRESHOLD = 2  # Threshold for considering a face as same unknown person

    def setup_background(self):
        try:
            bg_image = Image.open(bg_image_path)
            bg_image = bg_image.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(bg_image)
            
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()
        except Exception as e:
            print(f"Could not load background image: {e}")

    def hide_camera(self):
        """Hide the camera preview but keep the camera running"""
        if not self.running: return
        # Just hide the preview, don't stop the camera
        self.camera_panel.hide_camera_feed()

    def show_camera(self):
        """Show the camera preview"""
        if not self.running: return
        # Just show the preview, camera is already running
        self.camera_panel.show_camera_feed()

    def stop_camera(self):
        """Actually stop the camera (used for reset)"""
        if not self.running: return
        self.running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.camera_panel.show_grey_background()

    def update_frame(self):
        THRESHOLD = 0.50
        while self.running:
            try:
                if self.cap is None:
                    break
                    
                ret, frame = self.cap.read()
                if not ret: 
                    self.after(0, self.camera_init_failed)
                    break

                # Skip frames to reduce processing load
                self.skip_frames += 1
                if self.skip_frames % self.PROCESS_EVERY_N_FRAMES != 0:
                    # Still update the display if camera is visible
                    if self.camera_panel.is_camera_visible():
                        self.camera_panel.update_frame(frame)
                    continue

                # Process frame and detect faces even when preview is hidden
                small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                locs = face_recognition.face_locations(rgb_small)
                encs = face_recognition.face_encodings(rgb_small, locs)

                for enc, loc in zip(encs, locs):
                    distances = face_recognition.face_distance(encodeListKnown, enc)
                    best_idx = np.argmin(distances)
                    best_dist = distances[best_idx]

                    top, right, bottom, left = [v * 4 for v in loc]

                    if best_dist <= THRESHOLD:
                        name = studentNames[best_idx]
                        if name not in self.present_students:
                            self.present_students.add(name)
                            markAttendance(name)
                            color = self.face_colors[self.color_index % len(self.face_colors)]
                            self.color_index += 1
                            
                            # Update control panel stats with actual student count
                            self.control_panel.update_stats(
                                total_students=len(STUDENT_DATA),
                                marked_present=len(self.present_students),
                                unknown_detected=len(self.unknown_faces)  # Use unique unknown count
                            )
                            
                            # Get student image
                            image_path = get_student_image(name)
                            
                            # Create student card with all info
                            student_info = STUDENT_DATA.get(name.title(), {})
                            student_id = student_info.get('student_id', f"2023-{random.randint(10000, 99999)}")
                            self.students_panel.create_student_card(
                                student_id=student_id,
                                name=name.title(),
                                color=color,
                                student_info=student_info,
                                image_path=image_path
                            )
                        else:
                            color = self.face_colors[list(self.present_students).index(name) % len(self.face_colors)]

                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                        cv2.putText(frame, name, (left + 6, bottom - 6),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    else:
                        # Check if this unknown face has been seen before
                        is_new_unknown = True
                        unknown_enc = enc.copy()  # Make a copy of the encoding
                        
                        for known_unknown in self.unknown_faces:
                            # Compare with previously detected unknown faces
                            distance = face_recognition.face_distance([known_unknown], unknown_enc)[0]
                            if distance < self.UNKNOWN_FACE_THRESHOLD:
                                is_new_unknown = False
                                break
                        
                        if is_new_unknown:
                            self.unknown_faces.add(tuple(unknown_enc))  # Convert to tuple for set storage
                            self.unknown_count += 1
                            self.control_panel.update_stats(
                                total_students=len(STUDENT_DATA),
                                marked_present=len(self.present_students),
                                unknown_detected=len(self.unknown_faces)  # Use unique unknown count
                            )
                            
                        color = (128, 128, 128)
                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                        cv2.putText(frame, "UNKNOWN", (left + 6, bottom - 6),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                # Only update the camera panel if it's visible
                if self.camera_panel.is_camera_visible():
                    self.camera_panel.update_frame(frame)
                
            except Exception as e:
                print(f"Frame update error: {e}")
                self.after(0, self.camera_init_failed)
                break

        # Safely release camera if it exists
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def start_camera(self):
        if self.running: return
        
        # If camera was just stopped (paused), just restart the feed
        if self.cap is not None and self.cap.isOpened():
            self.running = True
            self.control_panel.camera_ready()
            threading.Thread(target=self.update_frame, daemon=True).start()
            return
        
        # Start camera initialization in a separate thread
        threading.Thread(target=self.initialize_camera, daemon=True).start()

    def initialize_camera(self):
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(0)
            
            # Check if camera is opened successfully
            if not self.cap.isOpened():
                self.after(0, self.camera_init_failed)
                return
                
            # Read first frame to ensure camera is working
            ret, _ = self.cap.read()
            if not ret:
                self.after(0, self.camera_init_failed)
                return
            
            # Camera initialized successfully
            self.after(0, self.camera_init_success)
            
        except Exception as e:
            print(f"Camera initialization error: {e}")
            self.after(0, self.camera_init_failed)

    def camera_init_success(self):
        # Update UI state
        self.running = True
        self.control_panel.camera_ready()
        
        # Start camera feed
        threading.Thread(target=self.update_frame, daemon=True).start()

    def camera_init_failed(self):
        """Handle camera initialization failure"""
        # Clean up camera if needed
        if self.cap:
            self.cap.release()
            self.cap = None
            
        # Reset states
        self.running = False
        self.camera_initialized = False
        
        # Notify control panel
        self.control_panel.camera_init_failed()

    def close_camera(self):
        """Completely reset the application state"""
        # First stop any running camera operations
        self.running = False
        
        # Wait a moment for the camera thread to stop
        self.after(100, self._complete_reset)
        
    def _complete_reset(self):
        """Complete the reset process after camera thread has stopped"""
        # Release and cleanup camera
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
        # Show camera emoji
        self.camera_panel.show_grey_background()
        
        # Clear student cards
        self.students_panel.clear_all_cards()
        
        # Reset detection variables
        self.present_students.clear()
        self.unknown_count = 0
        self.color_index = 0
        
        # Reset camera state
        self.camera_initialized = False
        
        # Reset control panel state
        self.control_panel.reset_state()
        
        # Update stats with correct total students
        self.control_panel.update_stats(
            total_students=len(STUDENT_DATA),
            marked_present=0,
            unknown_detected=0
        )

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print("\nShutting down gracefully...")
        self.quit()

    def on_closing(self):
        """Handle window closing"""
        print("Closing application...")
        self.close_camera()
        self.quit()

# GUI component imports (ensure these are available from app/components)
from app.components.control_panel import ControlPanel
from app.components.students_panel import StudentsPanel
from app.components.camera_panel import CameraPanel
from app.components.loading_window import LoadingWindow
from app.components.confirm_dialog import ConfirmDialog

if __name__ == '__main__':
    try:
        app = AttendanceApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down...")
        if hasattr(app, 'on_closing'):
            app.on_closing()
    finally:
        print("Application closed.")
