"""
Dashboard Page Component
Main dashboard with navigation sidebar and statistics overview
"""

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton
from datetime import datetime


class DashboardPage(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Setup navigation sidebar
        self.setup_navigation()
        
        # Setup main content
        self.setup_main_content()
        
        # Update timestamp
        self.update_timestamp()
    
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
            ("📊 Dashboard", "dashboard", True),  # Current page
            ("👥 Students", "students", False),
            ("📊 Attendance", "attendance", False),
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
        """Setup main dashboard content"""
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
            text="📊 Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=20)
        
        # Stats grid
        stats_frame = CTkFrame(content_frame)
        stats_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        stats_frame.grid_rowconfigure(1, weight=1)
        
        # Stats title
        stats_title = CTkLabel(
            stats_frame,
            text="System Statistics",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        stats_title.grid(row=0, column=0, columnspan=3, pady=(20, 10))
        
        # Stat cards
        self.create_stat_card(stats_frame, "👥 Total Students", "0", 1, 0)
        self.create_stat_card(stats_frame, "📷 Camera Status", "Offline", 1, 1)
        self.create_stat_card(stats_frame, "📊 Today's Attendance", "0", 1, 2)
        
        # Quick actions
        actions_frame = CTkFrame(content_frame)
        actions_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        actions_title = CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        actions_title.grid(row=0, column=0, columnspan=3, pady=(20, 10))
        
        # Action buttons
        start_camera_btn = CTkButton(
            actions_frame,
            text="📷 Start Camera",
            command=self.start_camera,
            width=150
        )
        start_camera_btn.grid(row=1, column=0, pady=10)
        
        view_reports_btn = CTkButton(
            actions_frame,
            text="📋 View Reports",
            command=self.view_reports,
            width=150
        )
        view_reports_btn.grid(row=1, column=1, pady=10)
        
        settings_btn = CTkButton(
            actions_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            width=150
        )
        settings_btn.grid(row=1, column=2, pady=10)
        
        # Recent activity
        activity_frame = CTkFrame(content_frame)
        activity_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        activity_frame.grid_columnconfigure(0, weight=1)
        
        activity_title = CTkLabel(
            activity_frame,
            text="Recent Activity",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        activity_title.grid(row=0, column=0, pady=(20, 10))
        
        # Activity list
        self.activity_text = CTkLabel(
            activity_frame,
            text="No recent activity",
            font=ctk.CTkFont(size=14)
        )
        self.activity_text.grid(row=1, column=0, pady=(0, 20))
    
    def create_stat_card(self, parent, title, value, row, col):
        """Create a statistics card"""
        card = CTkFrame(parent)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        
        title_label = CTkLabel(card, text=title, font=ctk.CTkFont(size=14))
        title_label.grid(row=0, column=0, pady=(15, 5))
        
        value_label = CTkLabel(
            card, 
            text=value, 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        value_label.grid(row=1, column=0, pady=(0, 15))
        
        # Store reference for updates
        if title == "👥 Total Students":
            self.students_count_label = value_label
        elif title == "📷 Camera Status":
            self.camera_status_label = value_label
        elif title == "📊 Today's Attendance":
            self.attendance_count_label = value_label
    
    def update_timestamp(self):
        """Update the timestamp display"""
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        self.activity_text.configure(text=f"Last updated: {timestamp}")
    
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
    
    def start_camera(self):
        """Start the camera system"""
        print("📷 Starting camera...")
        self.camera_status_label.configure(text="Online")
        # TODO: Implement camera start logic
    
    def view_reports(self):
        """Open reports view"""
        print("📋 Opening reports...")
        # TODO: Implement reports view
    
    def open_settings(self):
        """Open settings"""
        print("⚙️ Opening settings...")
        # TODO: Implement settings
