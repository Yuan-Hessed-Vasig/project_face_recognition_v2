"""
Main Application Class - Root
Serves as the base application for both main.py and dev.py
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import os
import atexit

# Set CustomTkinter theme and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

from app.ui.pages.home import HomePage
from app.ui.pages.login import LoginPage
from app.ui.pages.register import RegisterPage
from app.ui.pages.dashboard import DashboardPage
from app.ui.pages.students import StudentsPage
from app.ui.pages.attendance import AttendancePage
from app.utils.dev_state import DevStateManager, save_app_state, load_app_state


class Root(ctk.CTk):
    """Main Application Root Class"""
    
    def __init__(self, is_dev_mode=False):
        super().__init__()
        
        self.is_dev_mode = is_dev_mode
        self.dev_state_manager = DevStateManager()
        self.current_user = None  # Track logged in user
        
        # Initialize the application
        self.setup_window()
        self.setup_pages()
        
        # Load saved state if in dev mode
        if self.is_dev_mode:
            self.load_saved_state()
        
        # Show home page by default
        self.show_page("home")
        
        # Setup cleanup on exit
        atexit.register(self.cleanup)
    
    def setup_window(self):
        """Setup main window configuration"""
        self.title("Face Recognition Attendance System")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Development mode indicator
        if self.is_dev_mode:
            self.title("Face Recognition Attendance System - DEV MODE")
            print("🔥 Running in development mode")
    
    def setup_pages(self):
        """Setup all application pages"""
        # Main content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize pages
        self.pages = {
            "home": HomePage(self.content_frame, self),
            "dashboard": DashboardPage(self.content_frame),
            "students": StudentsPage(self.content_frame),
            "attendance": AttendancePage(self.content_frame),
            "login": LoginPage(self.content_frame, self),
            "register": RegisterPage(self.content_frame, self),
        }
        
        # Hide all pages initially
        for page in self.pages.values():
            page.grid_remove()
    
    def show_page(self, page_name):
        """Show the specified page"""
        if page_name not in self.pages:
            print(f"❌ Page '{page_name}' not found")
            return
        
        # Hide all pages
        for page in self.pages.values():
            page.grid_remove()
        
        # Show selected page
        selected_page = self.pages[page_name]
        selected_page.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Save current page to dev state
        if self.is_dev_mode:
            save_app_state("current_page", page_name)
        
        print(f"📄 Showing page: {page_name}")
    
    def show_main_app(self):
        """Show the main application after successful login"""
        self.show_page("dashboard")
    
    def logout(self):
        """Logout user and return to home page"""
        self.current_user = None
        self.show_page("home")
        print("🔓 User logged out")
    
    def set_current_user(self, username):
        """Set the currently logged in user"""
        self.current_user = username
        print(f"🔐 User logged in: {username}")
    
    def get_current_user(self):
        """Get the currently logged in user"""
        return self.current_user
    
    def load_saved_state(self):
        """Load saved application state"""
        try:
            # Load last visited page
            last_page = load_app_state("current_page", "home")
            if last_page in self.pages:
                self.show_page(last_page)
                print(f"💾 Restored to page: {last_page}")
            
            # Load other saved state as needed
            # TODO: Implement additional state restoration
            
        except Exception as e:
            print(f"⚠️  Error loading saved state: {e}")
    
    def cleanup(self):
        """Cleanup resources on exit"""
        try:
            if self.is_dev_mode:
                # Save current state
                self.dev_state_manager.save_state()
                print("💾 Saved dev state on exit")
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")


def run_app():
    """Main entry point for the application"""
    # Check if running in dev mode
    is_dev_mode = os.environ.get('DEV_MODE', 'false').lower() == 'true'
    
    if is_dev_mode:
        print("🔥 Starting Face Recognition Attendance System (Development Mode)")
        print("=" * 60)
        print("📁 Hot reload active - watching for file changes")
        print("🔄 App will automatically reload when Python files change")
        print("⏹️  Press Ctrl+C to stop")
        print("=" * 60)
    else:
        print("🚀 Starting Face Recognition Attendance System (Production Mode)")
        print("=" * 60)
    
    # Create and run the application
    app = Root(is_dev_mode=is_dev_mode)
    app.mainloop()


if __name__ == "__main__":
    run_app()
