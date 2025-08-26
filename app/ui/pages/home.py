"""
Home Page Component
Main landing page for the application with login/register buttons
"""

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton
import os
from pathlib import Path


class HomePage(CTkFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app_instance
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header with login/register buttons
        header_frame = CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        # App title (left side)
        title_label = CTkLabel(
            header_frame, 
            text="🎓 Face Recognition Attendance System",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=20, sticky="w")
        
        # Login/Register buttons (right side)
        auth_frame = CTkFrame(header_frame)
        auth_frame.grid(row=0, column=1, pady=20, padx=(20, 0))
        auth_frame.grid_columnconfigure((0, 1), weight=1)
        
        login_btn = CTkButton(
            auth_frame,
            text="🔐 Login",
            command=self.show_login,
            width=100,
            height=35
        )
        login_btn.grid(row=0, column=0, padx=(0, 10))
        
        register_btn = CTkButton(
            auth_frame,
            text="📝 Register",
            command=self.show_register,
            width=100,
            height=35
        )
        register_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Main content
        content_frame = CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Welcome message
        welcome_label = CTkLabel(
            content_frame,
            text="Welcome to the Face Recognition Attendance System",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        welcome_label.grid(row=0, column=0, pady=(40, 20))
        
        # Description
        desc_label = CTkLabel(
            content_frame,
            text="A modern, secure system for managing student attendance using facial recognition technology.",
            font=ctk.CTkFont(size=16),
            wraplength=600
        )
        desc_label.grid(row=1, column=0, pady=(0, 40))
        
        # Features section
        features_frame = CTkFrame(content_frame)
        features_frame.grid(row=2, column=0, pady=(0, 40))
        features_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Feature cards
        self.create_feature_card(features_frame, "📷 Face Recognition", "Advanced facial recognition for accurate attendance tracking", 0, 0)
        self.create_feature_card(features_frame, "📊 Real-time Monitoring", "Live attendance monitoring and reporting", 0, 1)
        self.create_feature_card(features_frame, "🔐 Secure Access", "User authentication and role-based access control", 0, 2)
        
        # Get started section
        get_started_frame = CTkFrame(content_frame)
        get_started_frame.grid(row=3, column=0, pady=(0, 40))
        get_started_frame.grid_columnconfigure(0, weight=1)
        
        get_started_label = CTkLabel(
            get_started_frame,
            text="Get Started",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        get_started_label.grid(row=0, column=0, pady=(20, 10))
        
        get_started_desc = CTkLabel(
            get_started_frame,
            text="Create an account or login to access the system",
            font=ctk.CTkFont(size=14)
        )
        get_started_desc.grid(row=1, column=0, pady=(0, 20))
        
        # Action buttons
        actions_frame = CTkFrame(content_frame)
        actions_frame.grid(row=4, column=0, pady=(0, 40))
        actions_frame.grid_columnconfigure((0, 1), weight=1)
        
        create_account_btn = CTkButton(
            actions_frame,
            text="Create Account",
            command=self.show_register,
            width=200,
            height=40
        )
        create_account_btn.grid(row=0, column=0, padx=10, pady=10)
        
        sign_in_btn = CTkButton(
            actions_frame,
            text="Sign In",
            command=self.show_login,
            width=200,
            height=40
        )
        sign_in_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Footer
        footer_frame = CTkFrame(content_frame)
        footer_frame.grid(row=5, column=0, sticky="ew", pady=(20, 0))
        footer_frame.grid_columnconfigure(0, weight=1)
        
        footer_label = CTkLabel(
            footer_frame,
            text="© 2024 Face Recognition Attendance System. All rights reserved.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        footer_label.grid(row=0, column=0, pady=20)
    
    def create_feature_card(self, parent, title, description, row, col):
        """Create a feature card"""
        card = CTkFrame(parent)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        
        title_label = CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, pady=(15, 10))
        
        desc_label = CTkLabel(
            card, 
            text=description, 
            font=ctk.CTkFont(size=14),
            wraplength=150
        )
        desc_label.grid(row=1, column=0, pady=(0, 15))
    
    def show_login(self):
        """Show login page"""
        self.app.show_page("login")
    
    def show_register(self):
        """Show register page"""
        self.app.show_page("register")
