import customtkinter as ctk
import sqlite3  # Added import
from datetime import datetime  # Added import

from database import db_setup, generate_sample_data
from ui.login_screen import LoginScreenMixin
from ui.main_screen import MainScreenMixin


class ClassRecordSystem(LoginScreenMixin, MainScreenMixin):
    def __init__(self, root):
        """Initialize Class Record System application"""
        self.root = root
        self.root.title("Class Record Management System")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        self.center_window(1400, 900)

        # Initialize user session variables
        self.current_user = None
        self.selected_subject = None
        self.current_attendance_section = "All Sections"
        self.current_stats_frame = None

        # Setup database and start login screen
        self.initialize_database()
        self.login_screen()

    def initialize_database(self):
        """Create and update database tables with sample data"""
        db_setup()
        
        # Check and update database schema if needed
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        
        try:
            # Check if password_hash column exists
            cur.execute("PRAGMA table_info(teachers)")
            columns = [column[1] for column in cur.fetchall()]
            
            if 'password_hash' not in columns:
                # Add password_hash column
                cur.execute("ALTER TABLE teachers ADD COLUMN password_hash TEXT")
                
                # Update existing teachers with default password
                from database import simple_hash_password
                default_password = simple_hash_password("password123")
                cur.execute("UPDATE teachers SET password_hash = ?", (default_password,))
                
                conn.commit()
                print("Database updated: Added password_hash column to teachers table")
                
            # Check if student_trash table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_trash'")
            if not cur.fetchone():
                # Create student_trash table
                cur.execute("""
                    CREATE TABLE student_trash (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_id TEXT,
                        student_id TEXT,
                        name TEXT,
                        grade_level INTEGER,
                        section TEXT,
                        subjects TEXT,
                        attendance TEXT,
                        deleted_at TEXT,
                        deleted_by TEXT
                    )
                """)
                conn.commit()
                print("Database updated: Created student_trash table")
                
        except Exception as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()
        
        # Generate sample data for testing
        generate_sample_data()

    def center_window(self, width, height):
        """Center application window on screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def change_appearance_mode(self, new_appearance_mode):
        """Change application theme (Light/Dark/System)"""
        ctk.set_appearance_mode(new_appearance_mode)

    def clear_main_content(self):
        """Clear main content area for new screens"""
        if hasattr(self, "main_content"):
            for widget in self.main_content.winfo_children():
                widget.destroy()
        self.current_stats_frame = None

    def clear_window(self):
        """Clear entire window for screen transitions"""
        for widget in self.root.winfo_children():
            widget.destroy()