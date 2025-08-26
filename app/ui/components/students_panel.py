import customtkinter as ctk
from PIL import Image, ImageTk
import os

class StudentsPanel:
    def __init__(self, parent):
        self.parent = parent
        self.student_cards = {}  # Dictionary to store student cards by ID
        
        # Students Panel Container
        self.container = ctk.CTkFrame(parent.main_content, corner_radius=15, fg_color=("gray92", "gray12"))
        self.container.grid(row=0, column=2, sticky="nsew", padx=5, pady=0)
        
        # Students Panel Label
        ctk.CTkLabel(self.container, text="Students Panel", font=("Arial Bold", 20)).pack(pady=(15, 20))

        # Create scrollable frame for student cards
        self.scrollable_frame = ctk.CTkScrollableFrame(self.container, corner_radius=10)
        self.scrollable_frame.pack(expand=True, fill="both", padx=10, pady=(0, 15))

    def create_student_card(self, student_id, name, color, student_info, image_path=None):
        # Check if card already exists
        if student_id in self.student_cards:
            return
            
        # Create card frame
        card = ctk.CTkFrame(self.scrollable_frame, corner_radius=10)
        card.pack(fill="x", padx=5, pady=5)
        
        # Color indicator
        color_frame = ctk.CTkFrame(card, width=10, height=80, corner_radius=5)
        color_frame.pack(side="left", padx=10, pady=10)
        color_frame.configure(fg_color=f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}")
        
        # Information frame
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        # Try to find a student image
        image_found = False
        if image_path is None:
            student_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                        "Images", "Students", name)
            if os.path.exists(student_folder):
                for file in os.listdir(student_folder):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_path = os.path.join(student_folder, file)
                        break

        # Load and display student image
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                img_label = ctk.CTkLabel(info_frame, image=photo, text="")
                img_label.image = photo  # Keep a reference
                img_label.pack(side="left", padx=(0, 10))
                image_found = True
            except Exception as e:
                print(f"Error loading image for {name}: {e}")

        if not image_found:
            img_label = ctk.CTkLabel(info_frame, text="No\nImage", width=60, height=60)
            img_label.pack(side="left", padx=(0, 10))

        # Student information
        text_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        
        # Student name
        ctk.CTkLabel(text_frame, text=name.title(), 
                    font=("Arial Bold", 14)).pack(anchor="w", pady=(0, 5))
        
        # Student ID
        ctk.CTkLabel(text_frame, text=f"ID: {student_id}", 
                    font=("Arial", 12)).pack(anchor="w", pady=2)
        
        # Course, Year, Section
        if isinstance(student_info, dict):
            if 'course' in student_info:
                ctk.CTkLabel(text_frame, text=f"Course: {student_info['course']}", 
                           font=("Arial", 12)).pack(anchor="w", pady=2)
            if 'year' in student_info:
                ctk.CTkLabel(text_frame, text=f"Year: {student_info['year']}", 
                           font=("Arial", 12)).pack(anchor="w", pady=2)
            if 'section' in student_info:
                ctk.CTkLabel(text_frame, text=f"Section: {student_info['section']}", 
                           font=("Arial", 12)).pack(anchor="w", pady=2)
        
        # Store card reference
        self.student_cards[student_id] = card

    def remove_student_card(self, student_id):
        if student_id in self.student_cards:
            self.student_cards[student_id].destroy()
            del self.student_cards[student_id]

    def update_student_card(self, name, is_present):
        """Update student card status"""
        # Find the student card by name
        for student_id, card in self.student_cards.items():
            # Check if this card belongs to the student
            if hasattr(card, 'student_name') and card.student_name == name:
                # Update the card appearance based on presence
                if is_present:
                    card.configure(fg_color=("lightgreen", "darkgreen"))
                else:
                    card.configure(fg_color=("gray92", "gray12"))
                break
    
    def clear_all_cards(self):
        for card in self.student_cards.values():
            card.destroy()
        self.student_cards.clear() 