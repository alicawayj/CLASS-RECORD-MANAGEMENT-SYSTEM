import customtkinter as ctk
from app import ClassRecordSystem

# Set application appearance
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

if __name__ == "__main__":
    # Create main window and start application
    root = ctk.CTk()
    app = ClassRecordSystem(root)
    root.mainloop()