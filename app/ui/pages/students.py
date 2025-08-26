"""
Students Page Component
Student management and information display with navigation sidebar
"""

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkTextbox, CTkEntry
import json
import os
from pathlib import Path


class StudentsPage(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Setup navigation sidebar
        self.setup_navigation()
        
        # Setup main content
        self.setup_main_content()
        
        # Load students
        self.load_students()
    
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
            ("👥 Students", "students", True),  # Current page
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
        """Setup main students content"""
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
            text="👥 Student Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=20)
        
        # Main content
        main_content_frame = CTkFrame(content_frame)
        main_content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_rowconfigure(1, weight=1)
        
        # Student list
        list_frame = CTkFrame(main_content_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        list_title = CTkLabel(
            list_frame,
            text="Student List",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        list_title.grid(row=0, column=0, pady=(20, 10))
        
        # Student listbox
        self.student_listbox = CTkTextbox(list_frame, height=400)
        self.student_listbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
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
        add_student_btn = CTkButton(
            actions_frame,
            text="➕ Add Student",
            command=self.add_student,
            width=150
        )
        add_student_btn.grid(row=1, column=0, pady=10)
        
        edit_student_btn = CTkButton(
            actions_frame,
            text="✏️ Edit Student",
            command=self.edit_student,
            width=150
        )
        edit_student_btn.grid(row=2, column=0, pady=10)
        
        delete_student_btn = CTkButton(
            actions_frame,
            text="🗑️ Delete Student",
            command=self.delete_student,
            width=150
        )
        delete_student_btn.grid(row=3, column=0, pady=10)
        
        refresh_btn = CTkButton(
            actions_frame,
            text="🔄 Refresh",
            command=self.refresh_students,
            width=150
        )
        refresh_btn.grid(row=4, column=0, pady=10)
    
    def load_students(self):
        """Load and display student list"""
        try:
            # Get app directory
            app_dir = Path(__file__).parent.parent.parent
            students_dir = app_dir / "Images" / "Students"
            students_json = students_dir / "students.json"
            
            if students_json.exists():
                with open(students_json, 'r') as f:
                    students = json.load(f)
                
                # Clear listbox
                self.student_listbox.delete("0.0", "end")
                
                # Display students
                for student in students:
                    name = student.get('name', 'Unknown')
                    self.student_listbox.insert("end", f"• {name}\n")
                
                print(f"✅ Loaded {len(students)} students")
            else:
                self.student_listbox.delete("0.0", "end")
                self.student_listbox.insert("0.0", "No students.json found")
                print("⚠️  No students.json found")
                
        except Exception as e:
            print(f"❌ Error loading students: {e}")
            self.student_listbox.delete("0.0", "end")
            self.student_listbox.insert("0.0", f"Error loading students: {e}")
    
    def refresh_students(self):
        """Refresh student list"""
        print("🔄 Refreshing student list...")
        self.load_students()
    
    def add_student(self):
        """Add a new student"""
        print("➕ Adding new student...")
        # TODO: Implement add student dialog
    
    def edit_student(self):
        """Edit selected student"""
        print("✏️ Editing student...")
        # TODO: Implement edit student dialog
    
    def delete_student(self):
        """Delete selected student"""
        print("🗑️ Deleting student...")
        # TODO: Implement delete student dialog
    
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
