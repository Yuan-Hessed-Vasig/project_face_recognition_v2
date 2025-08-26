import customtkinter as ctk

class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, on_yes=None, on_no=None, yes_text="Yes", no_text="No"):
        """
        Create a confirmation dialog.
        
        Args:
            parent: The parent window
            title: Dialog title
            message: Dialog message
            on_yes: Callback function when Yes is clicked
            on_no: Callback function when No is clicked
            yes_text: Custom text for Yes button
            no_text: Custom text for No button
        """
        super().__init__(parent)
        
        # Make dialog borderless
        self.overrideredirect(True)
        
        # Store callbacks
        self.on_yes = on_yes
        self.on_no = on_no
        
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
        
        # Add title
        self.title_label = ctk.CTkLabel(self.main_frame,
                                      text=title,
                                      font=("Arial Bold", 16))
        self.title_label.pack(pady=(15, 0))
        
        # Add message
        self.message_label = ctk.CTkLabel(self.main_frame, 
                                        text=message,
                                        font=("Arial", 14),
                                        wraplength=250)
        self.message_label.pack(pady=20)
        
        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.pack(pady=(0, 15))
        
        # Add buttons
        self.yes_button = ctk.CTkButton(self.buttons_frame, 
                                      text=yes_text,
                                      command=self.yes_clicked,
                                      fg_color="#FF6B6B",
                                      hover_color="#FF5252",
                                      width=100)
        self.yes_button.pack(side="left", padx=10)
        
        self.no_button = ctk.CTkButton(self.buttons_frame, 
                                     text=no_text,
                                     command=self.no_clicked,
                                     width=100)
        self.no_button.pack(side="left", padx=10)
        
        self.result = False
        
        # Bind escape key to close dialog
        self.bind("<Escape>", lambda e: self.no_clicked())
        
        # Make dialog draggable
        self.title_label.bind("<Button-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)
        
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
        
    def yes_clicked(self):
        self.result = True
        if self.on_yes:
            self.on_yes()
        self.destroy()
        
    def no_clicked(self):
        self.result = False
        if self.on_no:
            self.on_no()
        self.destroy()
        
    @staticmethod
    def show_dialog(parent, title, message, on_yes=None, on_no=None, yes_text="Yes", no_text="No"):
        """
        Static method to create and show a dialog, waiting for result.
        
        Returns:
            bool: True if Yes was clicked, False if No was clicked
        """
        dialog = ConfirmDialog(parent, title, message, on_yes, on_no, yes_text, no_text)
        parent.wait_window(dialog)
        return dialog.result 