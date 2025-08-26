"""
Register Page Component
User registration page with proper authentication service
"""

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkTextbox
from app.services.auth_service import register_user
import threading


class RegisterPage(CTkFrame):
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
            text="📝 Register",
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
        
        # Registration form
        form_frame = CTkFrame(self)
        form_frame.grid(row=1, column=0, sticky="n", padx=20, pady=20)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Full Name
        name_label = CTkLabel(form_frame, text="Full Name:")
        name_label.grid(row=0, column=0, pady=(20, 5), sticky="w")
        
        self.name_entry = CTkEntry(form_frame, placeholder_text="Enter full name")
        self.name_entry.grid(row=1, column=0, pady=(0, 20), sticky="ew", padx=20)
        
        # Username
        username_label = CTkLabel(form_frame, text="Username:")
        username_label.grid(row=2, column=0, pady=(0, 5), sticky="w")
        
        self.username_entry = CTkEntry(form_frame, placeholder_text="Enter username")
        self.username_entry.grid(row=3, column=0, pady=(0, 20), sticky="ew", padx=20)
        
        # Email
        email_label = CTkLabel(form_frame, text="Email:")
        email_label.grid(row=4, column=0, pady=(0, 5), sticky="w")
        
        self.email_entry = CTkEntry(form_frame, placeholder_text="Enter email")
        self.email_entry.grid(row=5, column=0, pady=(0, 20), sticky="ew", padx=20)
        
        # Password
        password_label = CTkLabel(form_frame, text="Password:")
        password_label.grid(row=6, column=0, pady=(0, 5), sticky="w")
        
        self.password_entry = CTkEntry(form_frame, placeholder_text="Enter password", show="*")
        self.password_entry.grid(row=7, column=0, pady=(0, 20), sticky="ew", padx=20)
        
        # Confirm Password
        confirm_password_label = CTkLabel(form_frame, text="Confirm Password:")
        confirm_password_label.grid(row=8, column=0, pady=(0, 5), sticky="w")
        
        self.confirm_password_entry = CTkEntry(form_frame, placeholder_text="Confirm password", show="*")
        self.confirm_password_entry.grid(row=9, column=0, pady=(0, 20), sticky="ew", padx=20)
        
        # Register button
        self.register_btn = CTkButton(
            form_frame,
            text="Register",
            command=self.register,
            width=200,
            height=40
        )
        self.register_btn.grid(row=10, column=0, pady=20)
        
        # Status message
        self.status_label = CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=11, column=0, pady=(0, 20))
        
        # Bind Enter key to next field
        self.name_entry.bind("<Return>", lambda e: self.username_entry.focus())
        self.username_entry.bind("<Return>", lambda e: self.email_entry.focus())
        self.email_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.confirm_password_entry.focus())
        self.confirm_password_entry.bind("<Return>", lambda e: self.register())
        
        # Focus on name field
        self.name_entry.focus()
    
    def register(self):
        """Handle registration logic"""
        name = self.name_entry.get().strip()
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validation
        if not all([name, username, email, password, confirm_password]):
            self.show_status("All fields are required.", "error")
            return
        
        if password != confirm_password:
            self.show_status("Passwords do not match.", "error")
            self.confirm_password_entry.delete(0, "end")
            self.confirm_password_entry.focus()
            return
        
        if len(username) < 3:
            self.show_status("Username must be at least 3 characters long.", "error")
            self.username_entry.focus()
            return
        
        if len(password) < 6:
            self.show_status("Password must be at least 6 characters long.", "error")
            self.password_entry.focus()
            return
        
        # Disable register button during registration
        self.register_btn.configure(state="disabled", text="Registering...")
        self.show_status("Creating account...", "info")
        
        # Run registration in separate thread to avoid blocking UI
        threading.Thread(target=self._register_user, args=(name, username, email, password), daemon=True).start()
    
    def _register_user(self, name: str, username: str, email: str, password: str):
        """Register user in background thread"""
        try:
            success, message = register_user(username, password, full_name=name, email=email)
            
            # Update UI in main thread
            self.after(0, self._handle_registration_result, success, message, username)
            
        except Exception as e:
            error_msg = f"Registration error: {str(e)}"
            self.after(0, self._handle_registration_result, False, error_msg, username)
    
    def _handle_registration_result(self, success: bool, message: str, username: str):
        """Handle registration result in main thread"""
        # Re-enable register button
        self.register_btn.configure(state="normal", text="Register")
        
        if success:
            self.show_status(message, "success")
            # Set current user in app
            self.app.set_current_user(username)
            # Clear form on successful registration
            self.clear_form()
            print(f"✅ Registration successful for user: {username}")
            # Redirect to main app
            self.app.show_main_app()
        else:
            self.show_status(message, "error")
            # Clear password fields on failed registration
            self.password_entry.delete(0, "end")
            self.confirm_password_entry.delete(0, "end")
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
        self.name_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.confirm_password_entry.delete(0, "end")
        self.status_label.configure(text="")
        self.name_entry.focus()
    
    def back_to_home(self):
        """Return to home page"""
        self.app.show_page("home")
