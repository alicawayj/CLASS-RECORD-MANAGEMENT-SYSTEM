import customtkinter as ctk
from tkinter import ttk
import sqlite3
from datetime import datetime

from .grades_tab import GradesTabMixin
from .attendance_tab import AttendanceTabMixin
from .update_tab import UpdateTabMixin
from .management_tab import ManagementMixin


class MainScreenMixin(
    GradesTabMixin,
    AttendanceTabMixin,
    UpdateTabMixin,
    ManagementMixin
):
    def main_screen(self):
        """Setup main dashboard with sidebar navigation and content area"""
        self.clear_window()

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Sidebar creation
        self.sidebar_frame = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar_frame,
            text=" CLASS RECORDS",
            font=("Arial", 20, "bold")
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            self.sidebar_frame,
            text=f"Welcome, {self.current_user[1]}",
            font=("Arial", 12),
            text_color=("gray50", "gray70")
        ).pack(pady=(0, 30))

        # Subject navigation section
        nav_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15)

        ctk.CTkLabel(
            nav_frame,
            text="SUBJECTS",
            font=("Arial", 12, "bold"),
            text_color=("gray50", "gray70")
        ).pack(anchor="w", pady=(10, 5))

        # Load teacher's subjects
        subjects = self.current_user[3].split(",") if self.current_user[3] else []
        for subject in subjects:
            if not subject:
                continue
            subject_btn = ctk.CTkButton(
                nav_frame,
                text=f"{subject}",
                command=lambda subj=subject: self.show_subject_dashboard(subj),
                fg_color="transparent",
                hover_color=("gray80", "gray30"),
                anchor="w",
                height=40
            )
            subject_btn.pack(fill="x", pady=2)

        # Management section
        ctk.CTkLabel(
            nav_frame,
            text="MANAGEMENT",
            font=("Arial", 12, "bold"),
            text_color=("gray50", "gray70")
        ).pack(anchor="w", pady=(20, 5))

        self.manage_subjects_btn = ctk.CTkButton(
            nav_frame,
            text="Manage Subjects",
            command=self.manage_subjects,
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            anchor="w",
            height=40
        )
        self.manage_subjects_btn.pack(fill="x", pady=2)

        # Appearance settings
        ctk.CTkLabel(
            self.sidebar_frame,
            text="APPEARANCE",
            font=("Arial", 12, "bold"),
            text_color=("gray50", "gray70")
        ).pack(anchor="w", pady=(30, 5), padx=15)

        appearance_mode = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode,
            width=220
        )
        appearance_mode.pack(pady=10, padx=15)

        # Main content area
        self.main_content = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.show_welcome_screen()

    def refresh_sidebar_subjects(self):
        """Update sidebar with current teacher's subject list"""
        if hasattr(self, "sidebar_frame"):
            for widget in self.sidebar_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    nav_frame = widget

                    # Find management label and button
                    management_label = None
                    manage_subjects_btn = None

                    for child in nav_frame.winfo_children():
                        if isinstance(child, ctk.CTkLabel) and "MANAGEMENT" in child.cget("text"):
                            management_label = child
                        elif isinstance(child, ctk.CTkButton) and child.cget("text") == "Manage Subjects":
                            manage_subjects_btn = child

                    # Clear existing subject buttons
                    to_destroy = []
                    for child in nav_frame.winfo_children():
                        if isinstance(child, ctk.CTkButton) and child != manage_subjects_btn:
                            to_destroy.append(child)

                    for btn in to_destroy:
                        btn.destroy()

                    # Get current subjects
                    subjects = self.current_user[3].split(",") if self.current_user[3] else []

                    # Add new subject buttons
                    if management_label:
                        for subject in subjects:
                            if not subject:
                                continue
                            subject_btn = ctk.CTkButton(
                                nav_frame,
                                text=f"{subject}",
                                command=lambda subj=subject: self.show_subject_dashboard(subj),
                                fg_color="transparent",
                                hover_color=("gray80", "gray30"),
                                anchor="w",
                                height=40
                            )
                            subject_btn.pack(fill="x", pady=2, before=management_label)
                    else:
                        for subject in subjects:
                            if not subject:
                                continue
                            subject_btn = ctk.CTkButton(
                                nav_frame,
                                text=f"{subject}",
                                command=lambda subj=subject: self.show_subject_dashboard(subj),
                                fg_color="transparent",
                                hover_color=("gray80", "gray30"),
                                anchor="w",
                                height=40
                            )
                            subject_btn.pack(fill="x", pady=2, before=manage_subjects_btn)

                    break

    def show_welcome_screen(self):
        """Display welcome screen with overall statistics"""
        self.clear_main_content()

        # Header
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header_frame,
            text="Welcome Back!",
            font=("Arial", 28, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Select a subject from the sidebar to manage student records",
            font=("Arial", 16),
            text_color=("gray50", "gray70")
        ).pack(anchor="w", pady=(5, 0))

        # Statistics cards
        stats_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()

        # Get statistics
        cur.execute("SELECT COUNT(DISTINCT student_id) FROM students")
        total_students = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM grades WHERE status = 'Failing'")
        failing_students = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM grades WHERE status = 'Dropped'")
        dropped_students = cur.fetchone()[0]

        current_date = datetime.now().strftime("%Y-%m-%d")
        cur.execute(
            "SELECT COUNT(*) FROM attendance WHERE status = 'A' AND date = ?",
            (current_date,)
        )
        total_absences = cur.fetchone()[0]

        conn.close()

        # Define stats data
        stats_data = [
            ("Students", total_students, "#2E8B57"),
            ("Failing", failing_students, "#DC143C"),
            ("Dropped", dropped_students, "#8B0000"),
            ("Absences", total_absences, "#FF8C00"),
            ("Subjects", len(self.current_user[3].split(",")), "#4169E1")
        ]

        # Create stat cards
        for i, (title, value, color) in enumerate(stats_data):
            card = ctk.CTkFrame(
                stats_frame,
                width=160,
                height=80,
                border_color=color,
                border_width=2,
                corner_radius=8
            )
            card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")
            card.grid_propagate(False)

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 11, "bold"),
                wraplength=140
            ).pack(pady=(8, 2))

            ctk.CTkLabel(
                card,
                text=str(value),
                font=("Arial", 18, "bold"),
                text_color=color
            ).pack(pady=(2, 8))

        stats_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

    def show_subject_dashboard(self, subject):
        """Display dashboard for selected subject with tabs"""
        self.selected_subject = subject
        self.clear_main_content()

        # Header with subject name
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header_frame,
            text=f"{subject} - Student Records",
            font=("Arial", 28, "bold")
        ).pack(anchor="w")

        # Subject-specific statistics
        self.current_stats_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.current_stats_frame.pack(fill="x", pady=(0, 20))

        self.create_stats_section(self.current_stats_frame)

        # Tabbed interface for different functions
        tabview = ctk.CTkTabview(self.main_content)
        tabview.pack(fill="both", expand=True, pady=10)

        tabview.add("Grades")
        tabview.add("Attendance")
        tabview.add("Update Records")

        # Setup each tab
        self.setup_grades_tab(tabview.tab("Grades"))
        self.setup_attendance_tab(tabview.tab("Attendance"))
        self.setup_update_tab(tabview.tab("Update Records"))

    def create_stats_section(self, stats_frame):
        """Create statistics cards for current subject"""
        for widget in stats_frame.winfo_children():
            widget.destroy()

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()

        # Get subject statistics
        cur.execute("""
            SELECT COUNT(*), AVG(final_grade), 
                   SUM(CASE WHEN status = 'Failing' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN status = 'Dropped' THEN 1 ELSE 0 END)
            FROM grades WHERE subject = ?
        """, (self.selected_subject,))
        result = cur.fetchone()
        total = result[0] if result else 0
        avg_grade = result[1] if result and result[1] else 0
        failing = result[2] if result else 0
        dropped = result[3] if result else 0

        # Get today's absences
        current_date = datetime.now().strftime("%Y-%m-%d")
        cur.execute("""
            SELECT COUNT(*) 
            FROM attendance 
            WHERE subject = ? AND status = 'A' AND date = ?
        """, (self.selected_subject, current_date))
        result = cur.fetchone()
        absences = result[0] if result else 0

        conn.close()

        # Define stats to display
        stats_data = [
            ("Students", total, "#2E8B57"),
            ("Avg Grade", f"{avg_grade:.1f}%" if avg_grade else "0.0%", "#4169E1"),
            ("Failing", failing, "#DC143C"),
            ("Dropped", dropped, "#8B0000"),
            ("Absences", absences, "#FF8C00")
        ]

        # Create stat cards
        for i, (title, value, color) in enumerate(stats_data):
            card = ctk.CTkFrame(
                stats_frame,
                width=160,
                height=80,
                border_color=color,
                border_width=2,
                corner_radius=8
            )
            card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")
            card.grid_propagate(False)

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 11, "bold"),
                wraplength=140
            ).pack(pady=(8, 2))

            ctk.CTkLabel(
                card,
                text=str(value),
                font=("Arial", 18, "bold"),
                text_color=color
            ).pack(pady=(2, 8))

        stats_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

    def refresh_dashboard_stats(self):
        """Update subject statistics display"""
        if self.selected_subject and self.current_stats_frame:
            self.create_stats_section(self.current_stats_frame) 