"""
Attendance Page Component
Attendance tracking and reporting with navigation sidebar
"""

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkTextbox, CTkEntry
import csv
import os
from pathlib import Path
from datetime import datetime


class AttendancePage(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Setup navigation sidebar
        self.setup_navigation()
        
        # Setup main content
        self.setup_main_content()
        
        # Load attendance
        self.load_attendance()
    
    def setup_navigation(self):
        """Setup navigation sidebar"""
        # Navigation frame
        nav_frame = ctk.CTkFrame(self, width=200)
        nav_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        nav_frame.grid_rowconfigure(1, weight=1)
        
        # App title
        title_label = ctk.CTkLabel(
            nav_frame,
            text="🎓 Attendance System",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=20)
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", "dashboard", False),
            ("👥 Students", "students", False),
            ("📊 Attendance", "attendance", True),  # Current page
        ]
        
        for i, (text, page_name, is_current) in enumerate(nav_buttons):
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                command=lambda p=page_name: self.navigate_to_page(p),
                width=180,
                height=35,
                fg_color=("blue", "darkblue") if is_current else None
            )
            btn.grid(row=i+1, column=0, pady=5, padx=10)
        
        # Logout button at bottom
        logout_btn = ctk.CTkButton(
            nav_frame,
            text="🔓 Logout",
            command=self.logout,
            width=180,
            height=35,
            fg_color="red"
        )
        logout_btn.grid(row=len(nav_buttons)+1, column=0, pady=20)
    
    def setup_main_content(self):
        """Setup main attendance content"""
        # Main content frame
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = CTkFrame(content_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = CTkLabel(
            header_frame, 
            text="📊 Attendance Tracking",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=20)
        
        # Main content
        main_content_frame = CTkFrame(content_frame)
        main_content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_rowconfigure(1, weight=1)
        
        # Attendance list
        list_frame = CTkFrame(main_content_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        list_title = CTkLabel(
            list_frame,
            text="Today's Attendance",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        list_title.grid(row=0, column=0, pady=(20, 10))
        
        # Attendance listbox
        self.attendance_listbox = CTkTextbox(list_frame, height=400)
        self.attendance_listbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Actions frame
        actions_frame = CTkFrame(main_content_frame)
        actions_frame.grid(row=0, column=1, sticky="n", padx=(10, 0))
        actions_frame.grid_columnconfigure(0, weight=1)
        
        actions_title = CTkLabel(
            actions_frame,
            text="Actions",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        actions_title.grid(row=0, column=0, pady=(20, 10))
        
        # Action buttons
        start_tracking_btn = CTkButton(
            actions_frame,
            text="📷 Start Tracking",
            command=self.start_tracking,
            width=150
        )
        start_tracking_btn.grid(row=1, column=0, pady=10)
        
        stop_tracking_btn = CTkButton(
            actions_frame,
            text="⏹️ Stop Tracking",
            command=self.stop_tracking,
            width=150
        )
        stop_tracking_btn.grid(row=2, column=0, pady=10)
        
        export_btn = CTkButton(
            actions_frame,
            text="📤 Export CSV",
            command=self.export_csv,
            width=150
        )
        export_btn.grid(row=3, column=0, pady=10)
        
        refresh_btn = CTkButton(
            actions_frame,
            text="🔄 Refresh",
            command=self.refresh_attendance,
            width=150
        )
        refresh_btn.grid(row=4, column=0, pady=10)
        
        # Status indicator
        self.status_label = CTkLabel(
            actions_frame,
            text="Status: Stopped",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=5, column=0, pady=(20, 0))
    
    def load_attendance(self):
        """Load and display attendance data"""
        try:
            # Get app directory
            app_dir = Path(__file__).parent.parent.parent
            attendance_file = app_dir / "attendance.csv"
            
            if attendance_file.exists():
                with open(attendance_file, 'r') as f:
                    reader = csv.DictReader(f)
                    attendance_records = list(reader)
                
                # Clear listbox
                self.attendance_listbox.delete("0.0", "end")
                
                if attendance_records:
                    # Display attendance records
                    for record in attendance_records:
                        name = record.get('Name', 'Unknown')
                        timestamp = record.get('Timestamp', 'Unknown')
                        self.attendance_listbox.insert("end", f"• {name} - {timestamp}\n")
                    
                    print(f"✅ Loaded {len(attendance_records)} attendance records")
                else:
                    self.attendance_listbox.insert("0.0", "No attendance records found")
                    print("⚠️  No attendance records found")
            else:
                self.attendance_listbox.delete("0.0", "end")
                self.attendance_listbox.insert("0.0", "No attendance file found")
                print("⚠️  No attendance.csv found")
                
        except Exception as e:
            print(f"❌ Error loading attendance: {e}")
            self.attendance_listbox.delete("0.0", "end")
            self.attendance_listbox.insert("0.0", f"Error loading attendance: {e}")
    
    def start_tracking(self):
        """Start attendance tracking"""
        print("📷 Starting attendance tracking...")
        self.status_label.configure(text="Status: Tracking")
        # TODO: Implement tracking start logic
    
    def stop_tracking(self):
        """Stop attendance tracking"""
        print("⏹️ Stopping attendance tracking...")
        self.status_label.configure(text="Status: Stopped")
        # TODO: Implement tracking stop logic
    
    def export_csv(self):
        """Export attendance data to CSV"""
        print("📤 Exporting attendance data...")
        # TODO: Implement CSV export logic
    
    def refresh_attendance(self):
        """Refresh attendance display"""
        print("🔄 Refreshing attendance data...")
        self.load_attendance()
    
    def navigate_to_page(self, page_name):
        """Navigate to a different page"""
        # Get the app instance from the master
        app = self.master.master
        if hasattr(app, 'show_page'):
            app.show_page(page_name)
    
    def logout(self):
        """Logout user and return to home"""
        app = self.master.master
        if hasattr(app, 'logout'):
            app.logout()
