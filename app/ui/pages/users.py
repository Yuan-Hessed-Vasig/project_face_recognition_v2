"""
Users Page Component
User management and display page
"""

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkTextbox, CTkEntry
from app.services.auth_service import list_users, get_user_info, delete_user
import threading


class UsersPage(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = CTkLabel(
            header_frame, 
            text="👥 User Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=20)
        
        # Main content
        content_frame = CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Users list
        list_frame = CTkFrame(content_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        list_title = CTkLabel(
            list_frame,
            text="Registered Users",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        list_title.grid(row=0, column=0, pady=(20, 10))
        
        # Users listbox
        self.users_listbox = CTkTextbox(list_frame, height=400)
        self.users_listbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Actions frame
        actions_frame = CTkFrame(content_frame)
        actions_frame.grid(row=0, column=1, sticky="n", padx=(10, 0))
        actions_frame.grid_columnconfigure(0, weight=1)
        
        actions_title = CTkLabel(
            actions_frame,
            text="Actions",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        actions_title.grid(row=0, column=0, pady=(20, 10))
        
        # Action buttons
        refresh_btn = CTkButton(
            actions_frame,
            text="🔄 Refresh",
            command=self.refresh_users,
            width=150
        )
        refresh_btn.grid(row=1, column=0, pady=10)
        
        view_user_btn = CTkButton(
            actions_frame,
            text="👁️ View User",
            command=self.view_selected_user,
            width=150
        )
        view_user_btn.grid(row=2, column=0, pady=10)
        
        delete_user_btn = CTkButton(
            actions_frame,
            text="🗑️ Delete User",
            command=self.delete_selected_user,
            width=150
        )
        delete_user_btn.grid(row=3, column=0, pady=10)
        
        # Status indicator
        self.status_label = CTkLabel(
            actions_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=4, column=0, pady=(20, 0))
        
        # Load users
        self.load_users()
    
    def load_users(self):
        """Load and display user list"""
        try:
            success, message, usernames = list_users()
            
            # Clear listbox
            self.users_listbox.delete("0.0", "end")
            
            if success and usernames:
                # Display users
                for username in usernames:
                    self.users_listbox.insert("end", f"• {username}\n")
                
                self.show_status(f"✅ {message}", "success")
                print(f"✅ Loaded {len(usernames)} users")
            else:
                self.users_listbox.insert("0.0", "No users found")
                self.show_status(message, "info")
                print("⚠️  No users found")
                
        except Exception as e:
            print(f"❌ Error loading users: {e}")
            self.users_listbox.delete("0.0", "end")
            self.users_listbox.insert("0.0", f"Error loading users: {e}")
            self.show_status(f"Error: {e}", "error")
    
    def refresh_users(self):
        """Refresh user list"""
        print("🔄 Refreshing user list...")
        self.load_users()
    
    def view_selected_user(self):
        """View details of selected user"""
        # Get selected text (simple selection for now)
        selected_text = self.users_listbox.get("1.0", "end").strip()
        if not selected_text or selected_text == "No users found":
            self.show_status("No users to view", "error")
            return
        
        # Get first user for demo (in real app, you'd get the selected user)
        lines = selected_text.split('\n')
        if lines and lines[0].startswith('• '):
            username = lines[0][2:]  # Remove "• " prefix
            self.show_user_details(username)
        else:
            self.show_status("Please select a user to view", "error")
    
    def show_user_details(self, username: str):
        """Show detailed user information"""
        try:
            success, message, user_data = get_user_info(username)
            
            if success:
                # Create a simple popup with user info
                details_text = f"User: {username}\n"
                for key, value in user_data.items():
                    if key != 'password_hash':  # Don't show password hash
                        details_text += f"{key}: {value}\n"
                
                self.show_status(f"User details loaded for {username}", "success")
                print(f"✅ User details: {details_text}")
            else:
                self.show_status(f"Failed to load user details: {message}", "error")
                
        except Exception as e:
            print(f"❌ Error viewing user: {e}")
            self.show_status(f"Error: {e}", "error")
    
    def delete_selected_user(self):
        """Delete selected user"""
        # Get selected text (simple selection for now)
        selected_text = self.users_listbox.get("1.0", "end").strip()
        if not selected_text or selected_text == "No users found":
            self.show_status("No users to delete", "error")
            return
        
        # Get first user for demo (in real app, you'd get the selected user)
        lines = selected_text.split('\n')
        if lines and lines[0].startswith('• '):
            username = lines[0][2:]  # Remove "• " prefix
            self.confirm_delete_user(username)
        else:
            self.show_status("Please select a user to delete", "error")
    
    def confirm_delete_user(self, username: str):
        """Confirm user deletion"""
        # Simple confirmation dialog
        self.show_status(f"Click delete again to confirm deletion of {username}", "info")
        
        # In a real app, you'd show a proper confirmation dialog
        # For now, we'll just show a message
        print(f"🗑️ User deletion requested for: {username}")
        self.show_status(f"Deletion requested for {username}. Implement confirmation dialog.", "info")
    
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
