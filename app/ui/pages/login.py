"""
Login Page Component
User authentication page with proper authentication service
"""

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkTextbox
from app.services.auth_service import login_user
import threading


class LoginPage(CTkFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app_instance
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = CTkLabel(
            header_frame, 
            text="🔐 Login",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=20)
        
        # Back to home button
        back_btn = CTkButton(
            header_frame,
            text="🏠 Back to Home",
            command=self.back_to_home,
            width=120,
            height=30
        )
        back_btn.grid(row=0, column=1, pady=20, padx=(20, 0))
        
        # Login form
        form_frame = CTkFrame(self)
        form_frame.grid(row=1, column=0, sticky="n", padx=20, pady=20)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Username
        username_label = CTkLabel(form_frame, text="Username:")
        username_label.grid(row=0, column=0, pady=(20, 5), sticky="w")
        
        self.username_entry = CTkEntry(form_frame, placeholder_text="Enter username")
        self.username_entry.grid(row=1, column=0, pady=(0, 20), sticky="ew", padx=20)
        
        # Password
        password_label = CTkLabel(form_frame, text="Password:")
        password_label.grid(row=2, column=0, pady=(0, 5), sticky="w")
        
        self.password_entry = CTkEntry(form_frame, placeholder_text="Enter password", show="*")
        self.password_entry.grid(row=3, column=0, pady=(0, 20), sticky="ew", padx=20)
        
        # Login button
        self.login_btn = CTkButton(
            form_frame,
            text="Login",
            command=self.login,
            width=200,
            height=40
        )
        self.login_btn.grid(row=4, column=0, pady=20)
        
        # Status message
        self.status_label = CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=5, column=0, pady=(0, 20))
        
        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        # Focus on username field
        self.username_entry.focus()
    
    def login(self):
        """Handle login logic"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_status("Please enter both username and password.", "error")
            return
        
        # Disable login button during authentication
        self.login_btn.configure(state="disabled", text="Logging in...")
        self.show_status("Authenticating...", "info")
        
        # Run authentication in separate thread to avoid blocking UI
        threading.Thread(target=self._authenticate, args=(username, password), daemon=True).start()
    
    def _authenticate(self, username: str, password: str):
        """Authenticate user in background thread"""
        try:
            success, message = login_user(username, password)
            
            # Update UI in main thread
            self.after(0, self._handle_auth_result, success, message, username)
            
        except Exception as e:
            error_msg = f"Authentication error: {str(e)}"
            self.after(0, self._handle_auth_result, False, error_msg, username)
    
    def _handle_auth_result(self, success: bool, message: str, username: str):
        """Handle authentication result in main thread"""
        # Re-enable login button
        self.login_btn.configure(state="normal", text="Login")
        
        if success:
            self.show_status(message, "success")
            # Set current user in app
            self.app.set_current_user(username)
            # Clear password field
            self.password_entry.delete(0, "end")
            # Redirect to main app
            self.app.show_main_app()
            print(f"✅ Login successful for user: {username}")
        else:
            self.show_status(message, "error")
            # Clear password field on failed login
            self.password_entry.delete(0, "end")
            self.password_entry.focus()
    
    def show_status(self, message: str, status_type: str = "info"):
        """Show status message with appropriate styling"""
        self.status_label.configure(text=message)
        
        # Set color based on status type
        if status_type == "success":
            self.status_label.configure(text_color="green")
        elif status_type == "error":
            self.status_label.configure(text_color="red")
        elif status_type == "info":
            self.status_label.configure(text_color="blue")
        else:
            self.status_label.configure(text_color="white")
    
    def clear_form(self):
        """Clear all form fields"""
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.status_label.configure(text="")
        self.username_entry.focus()
    
    def back_to_home(self):
        """Return to home page"""
        self.app.show_page("home")
