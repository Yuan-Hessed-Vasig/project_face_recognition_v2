import customtkinter as ctk
from .confirm_dialog import ConfirmDialog
from .loading_window import LoadingWindow

class ControlPanel:
    def __init__(self, parent):
        self.parent = parent
        self.loading_window = None
        
        # Control Panel Container
        self.container = ctk.CTkFrame(parent.main_content, corner_radius=15, fg_color=("gray92", "gray12"))
        self.container.grid(row=0, column=0, sticky="nsew", padx=5, pady=0)
        
        # Control Panel Label
        ctk.CTkLabel(self.container, text="Control Panel", font=("Arial Bold", 20)).pack(pady=(15, 20))

        # Create content container
        self.content = ctk.CTkFrame(self.container, corner_radius=10, fg_color="transparent")
        self.content.pack(expand=True, fill="both", padx=10, pady=(0, 15))

        # Buttons Container
        self.buttons_container = ctk.CTkFrame(self.content, corner_radius=10)
        self.buttons_container.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(self.buttons_container, text="Camera Control", font=("Arial Bold", 14)).pack(pady=(10, 5))
        
        # Camera control buttons
        self.start_stop_button = ctk.CTkButton(self.buttons_container, text="▶️ Start Camera", command=self.toggle_camera)
        self.start_stop_button.pack(padx=10, pady=5)

        self.reset_button = ctk.CTkButton(self.buttons_container, text="Full Reset",
                                       command=self.confirm_reset, 
                                       fg_color="#FF6B6B",
                                       hover_color="#FF5252")
        self.reset_button.pack(padx=10, pady=(5, 10))

        # Status Container
        self.status_container = ctk.CTkFrame(self.content, corner_radius=10)
        self.status_container.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(self.status_container, text="System Status", 
                    font=("Arial Bold", 14)).pack(pady=(10, 5))
        
        self.status_label = ctk.CTkLabel(self.status_container, text="Camera Offline",
                                       font=("Arial", 12))
        self.status_label.pack(pady=(0, 10))

        # Live Stats Container
        self.stats_container = ctk.CTkFrame(self.content, corner_radius=10)
        self.stats_container.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(self.stats_container, text="Live Statistics", 
                    font=("Arial Bold", 14)).pack(pady=(10, 5))
        
        # Stats grid
        stats_grid = ctk.CTkFrame(self.stats_container, fg_color="transparent")
        stats_grid.pack(fill="x", padx=10, pady=(0, 10))
        
        # Total Students
        ctk.CTkLabel(stats_grid, text="Total Students:", 
                    font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=2)
        self.total_students_label = ctk.CTkLabel(stats_grid, text="0",
                                               font=("Arial", 12))
        self.total_students_label.grid(row=0, column=1, sticky="e")
        
        # Marked Present
        ctk.CTkLabel(stats_grid, text="Marked Present:", 
                    font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=2)
        self.marked_present_label = ctk.CTkLabel(stats_grid, text="0",
                                               font=("Arial", 12))
        self.marked_present_label.grid(row=1, column=1, sticky="e")
        
        # Unknown Detected
        ctk.CTkLabel(stats_grid, text="Unknown Detected:", 
                    font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=2)
        self.unknown_detected_label = ctk.CTkLabel(stats_grid, text="0",
                                                font=("Arial", 12))
        self.unknown_detected_label.grid(row=2, column=1, sticky="e")
        
        # Configure grid weights
        stats_grid.grid_columnconfigure(1, weight=1)

        # Window Control Buttons
        window_controls = ctk.CTkFrame(self.container, fg_color="transparent")
        window_controls.pack(side="bottom", fill="x", padx=10, pady=10)

        self.minimize_btn = ctk.CTkButton(window_controls, 
                                        text="—",
                                        width=40,
                                        height=30,
                                        command=self.minimize_window,
                                        fg_color=("gray85", "gray25"),
                                        hover_color=("gray75", "gray35"))
        self.minimize_btn.pack(side="left", padx=5)

        self.maximize_btn = ctk.CTkButton(window_controls, 
                                        text="□",
                                        width=40,
                                        height=30,
                                        command=self.toggle_maximize,
                                        fg_color=("gray85", "gray25"),
                                        hover_color=("gray75", "gray35"))
        self.maximize_btn.pack(side="left", padx=5)

        self.close_btn = ctk.CTkButton(window_controls, 
                                     text="✕",
                                     width=40,
                                     height=30,
                                     command=self.close_window,
                                     fg_color="#FF0000",
                                     hover_color="#CC0000",
                                     text_color="white")
        self.close_btn.pack(side="left", padx=5)

        # Track camera state
        self.camera_running = False

    def toggle_camera(self):
        if not self.camera_running:
            # Starting camera for the first time
            self.start_stop_button.configure(state="disabled")
            self.reset_button.configure(state="disabled")
            
            # Show loading window
            self.loading_window = LoadingWindow(
                self.parent,
                message="Initializing Camera...",
                progress_mode="indeterminate"
            )
            
            if hasattr(self.parent, 'start_camera'):
                self.parent.start_camera()
        else:
            # Toggle camera visibility
            current_text = self.start_stop_button.cget("text")
            if current_text == "⛔ Hide Camera":
                # Hide camera preview
                self.start_stop_button.configure(text="👁️ Show Camera")
                self.status_label.configure(text="Camera Hidden (Still Running)")
                if hasattr(self.parent, 'hide_camera'):
                    self.parent.hide_camera()
            else:
                # Show camera preview
                self.start_stop_button.configure(text="⛔ Hide Camera")
                self.status_label.configure(text="Camera Online")
                if hasattr(self.parent, 'show_camera'):
                    self.parent.show_camera()

    def camera_ready(self):
        """Called when camera is successfully initialized"""
        # Close loading window if it exists
        if self.loading_window:
            self.loading_window.stop()
            self.loading_window = None
            
        self.start_stop_button.configure(state="normal", text="⛔ Hide Camera")
        self.reset_button.configure(state="normal")
        self.status_label.configure(text="Camera Online")
        self.camera_running = True
        # Show camera preview initially
        if hasattr(self.parent, 'show_camera'):
            self.parent.show_camera()

    def camera_init_failed(self):
        """Called when camera initialization fails"""
        # Close loading window if it exists
        if self.loading_window:
            self.loading_window.stop()
            self.loading_window = None
            
        self.start_stop_button.configure(state="normal", text="▶️ Start Camera")
        self.reset_button.configure(state="normal")
        self.status_label.configure(text="Camera Initialization Failed")
        self.camera_running = False

    def close_camera(self):
        """Close and release the camera, reset all states and enable reinitialization"""
        # Reset camera state
        self.camera_running = False
        
        # Reset button states
        self.start_stop_button.configure(text="▶️ Start Camera")
        
        # Reset status
        self.status_label.configure(text="Camera Offline")
        
        # Reset stats
        self.update_stats(total_students=0, marked_present=0, unknown_detected=0)
        
        # Call parent's close_camera to handle camera release and other cleanup
        if hasattr(self.parent, 'close_camera'):
            self.parent.close_camera()
            
        # Reset camera initialization state
        if hasattr(self.parent, 'camera_initialized'):
            self.parent.camera_initialized = False
            
        # Reset running state
        if hasattr(self.parent, 'running'):
            self.parent.running = False
            
        # Stop camera if it's running
        if hasattr(self.parent, 'stop_camera'):
            self.parent.stop_camera()

    def update_stats(self, total_students=0, marked_present=0, unknown_detected=0):
        self.total_students_label.configure(text=str(total_students))
        self.marked_present_label.configure(text=str(marked_present))
        self.unknown_detected_label.configure(text=str(unknown_detected))

    def minimize_window(self):
        self.parent.iconify()

    def toggle_maximize(self):
        if self.parent.wm_state() == 'zoomed':
            self.parent.wm_state('normal')
            self.maximize_btn.configure(text="□")
        else:
            self.parent.wm_state('zoomed')
            self.maximize_btn.configure(text="❐")

    def close_window(self):
        if hasattr(self.parent, 'on_closing'):
            self.parent.on_closing()
        else:
            self.parent.quit()

    def confirm_reset(self):
        """Show confirmation dialog for reset action"""
        result = ConfirmDialog.show_dialog(
            parent=self.parent,
            title="Confirm Reset",
            message="Are you sure you want to reset? This will close the camera and clear all data.",
            on_yes=self.close_camera,
            yes_text="Reset",
            no_text="Cancel"
        )

    def reset_state(self):
        """Reset the control panel to its initial state"""
        # Close loading window if it exists
        if self.loading_window:
            self.loading_window.stop()
            self.loading_window = None
            
        # Reset camera running state
        self.camera_running = False
        
        # Reset button states and text
        self.start_stop_button.configure(
            text="▶️ Start Camera",
            state="normal"
        )
        self.reset_button.configure(state="normal")
        
        # Reset status
        self.status_label.configure(text="Camera Offline")
        
        # Reset stats
        self.update_stats(
            total_students=0,  # This will be updated by AttendanceApp
            marked_present=0,
            unknown_detected=0
        ) 