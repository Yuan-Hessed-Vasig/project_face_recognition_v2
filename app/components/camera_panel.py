import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import numpy as np

class CameraPanel:
    def __init__(self, parent):
        self.parent = parent
        self.camera_visible = False
        
        # Camera Panel Container
        self.container = ctk.CTkFrame(parent.main_content, corner_radius=15, fg_color=("gray92", "gray12"))
        self.container.grid(row=0, column=1, sticky="nsew", padx=5, pady=0)
        
        # Camera Panel Label
        ctk.CTkLabel(self.container, text="Camera Panel", 
                    font=("Arial Bold", 20)).pack(pady=(15, 20))

        # Camera Frame
        self.camera_frame = ctk.CTkFrame(self.container, corner_radius=10, fg_color="transparent")
        self.camera_frame.pack(expand=True, fill="both", padx=10, pady=(0, 15))
        
        # Camera Content Frame
        self.content_frame = ctk.CTkFrame(self.camera_frame, corner_radius=10)
        self.content_frame.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Create placeholder frame for camera emoji
        self.placeholder_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.placeholder_frame.pack(expand=True, fill="both", padx=15, pady=15)
        
        # Camera emoji label
        self.emoji_label = ctk.CTkLabel(self.placeholder_frame, 
                                      text="📷", 
                                      font=("Arial", 120),
                                      fg_color=("gray85", "gray20"),
                                      corner_radius=10)
        self.emoji_label.pack(expand=True, fill="both")
        
        # Camera Label for displaying video feed (initially hidden)
        self.camera_label = ctk.CTkLabel(self.content_frame, text="")
        self.camera_label.pack(expand=True, fill="both", padx=15, pady=15)
        self.camera_label.pack_forget()  # Hide initially
        
        # Loading Label
        self.loading_label = ctk.CTkLabel(self.content_frame, 
                                        text="Wait lang. Nag-iisip pako...", 
                                        font=("Arial", 16))
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.loading_label.lower()  # Initially hidden behind camera feed

        # Show initial grey background
        self.show_grey_background()

    def update_frame(self, frame):
        if frame is not None:
            # Show camera label and hide placeholder
            if not self.camera_label.winfo_ismapped():
                self.placeholder_frame.pack_forget()
                self.camera_label.pack(expand=True, fill="both", padx=15, pady=15)
            
            # Convert frame to PhotoImage
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            
            # Calculate new size maintaining aspect ratio
            display_width = self.content_frame.winfo_width() - 30  # Account for padding
            display_height = self.content_frame.winfo_height() - 30
            
            if display_width > 0 and display_height > 0:
                # Calculate scaling factor
                frame_ratio = frame.width / frame.height
                display_ratio = display_width / display_height
                
                if frame_ratio > display_ratio:
                    # Width limited
                    new_width = display_width
                    new_height = int(display_width / frame_ratio)
                else:
                    # Height limited
                    new_height = display_height
                    new_width = int(display_height * frame_ratio)
                
                frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(frame)
            self.camera_label.configure(image=photo)
            self.camera_label.image = photo  # Keep a reference
            
            # Hide loading label when frame is shown
            self.loading_label.lower()
        else:
            # Show loading label when no frame
            self.loading_label.lift()

    def show_loading(self, show=True, message="Wait lang. Nag-iisip pako..."):
        self.loading_label.configure(text=message)
        if show:
            self.loading_label.lift()
        else:
            self.loading_label.lower()

    def is_camera_visible(self):
        """Check if camera preview is currently visible"""
        return self.camera_visible

    def hide_camera_feed(self):
        """Hide camera feed and show emoji"""
        self.camera_visible = False
        self.camera_label.pack_forget()
        self.placeholder_frame.pack(expand=True, fill="both", padx=15, pady=15)

    def show_camera_feed(self):
        """Show camera feed and hide emoji"""
        self.camera_visible = True
        self.placeholder_frame.pack_forget()
        self.camera_label.pack(expand=True, fill="both", padx=15, pady=15)

    def show_grey_background(self):
        """Show grey background with emoji (used when camera is stopped)"""
        self.camera_visible = False
        self.camera_label.pack_forget()
        self.placeholder_frame.pack(expand=True, fill="both", padx=15, pady=15) 