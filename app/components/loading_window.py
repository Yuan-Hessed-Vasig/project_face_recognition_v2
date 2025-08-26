import customtkinter as ctk

class LoadingWindow(ctk.CTkToplevel):
    def __init__(self, parent, message="Loading...", progress_mode="indeterminate"):
        """
        Create a loading window.
        
        Args:
            parent: The parent window
            message: Loading message to display
            progress_mode: "indeterminate" for continuous animation or "determinate" for specific progress
        """
        super().__init__(parent)
        
        # Make window borderless
        self.overrideredirect(True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
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
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create main frame with shadow effect
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("gray95", "gray10"))
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Add loading message
        self.message_label = ctk.CTkLabel(self.main_frame, 
                                        text=message,
                                        font=("Arial", 14))
        self.message_label.pack(pady=(30, 20))
        
        # Add progress bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=200)
        self.progress_bar.pack(pady=(0, 30))
        
        if progress_mode == "indeterminate":
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
        else:
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(0)
            
    def update_message(self, message):
        """Update the loading message"""
        self.message_label.configure(text=message)
        
    def update_progress(self, value):
        """Update progress bar value (0-1) for determinate mode"""
        if self.progress_bar.cget("mode") == "determinate":
            self.progress_bar.set(value)
            
    def stop(self):
        """Stop the progress bar animation and destroy the window"""
        if self.progress_bar.cget("mode") == "indeterminate":
            self.progress_bar.stop()
        self.destroy() 