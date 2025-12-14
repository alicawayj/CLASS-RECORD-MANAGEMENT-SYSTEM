import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


class AttendanceTabMixin:
    def setup_attendance_tab(self, parent):
        """Create attendance tracking interface with date selection and marking controls"""
        date_frame = ctk.CTkFrame(parent, fg_color="transparent")
        date_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(date_frame, text="Select Date:", font=("Arial", 14)).pack(side="left", padx=(0, 10))

        self.attendance_date = ctk.CTkEntry(
            date_frame,
            placeholder_text="YYYY-MM-DD",
            width=150
        )
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.attendance_date.insert(0, current_date)
        self.attendance_date.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            date_frame,
            text="Load Attendance",
            command=self.load_attendance_data,
            width=150,
            height=35
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            date_frame,
            text="Refresh Stats",
            command=self.refresh_dashboard_stats,
            width=120,
            height=35,
            fg_color="#4169E1"
        ).pack(side="left", padx=(0, 10))

        # Section filter
        ctk.CTkLabel(date_frame, text="Section:", font=("Arial", 14)).pack(side="left", padx=(10, 10))
        self.attendance_section_filter = ctk.CTkComboBox(
            date_frame,
            values=["All Sections"],
            width=150
        )
        self.attendance_section_filter.set("All Sections")
        self.attendance_section_filter.pack(side="left", padx=(0, 10))
        self.attendance_section_filter.bind("<<ComboboxSelected>>", self.filter_attendance)

        self.load_attendance_section_filter()

        # Attendance table
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill="both", expand=True, pady=10)

        tree_container = ctk.CTkFrame(table_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Name", "Grade Level", "Section", "Status", "Mark")
        self.attendance_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)

        column_config = {
            "ID": 80,
            "Name": 200,
            "Grade Level": 100,
            "Section": 120,
            "Status": 120,
            "Mark": 80
        }

        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=column_config[col])

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)

        self.attendance_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Marking buttons
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            button_frame,
            text="Mark Selected as Present (P)",
            command=lambda: self.bulk_mark_attendance("P"),
            fg_color="#2E8B57",
            hover_color="#1F5E3A",
            height=40
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Mark Selected as Absent (A)",
            command=lambda: self.bulk_mark_attendance("A"),
            fg_color="#DC143C",
            hover_color="#B22222",
            height=40
        ).pack(side="left", padx=5)

        self.load_attendance_data()

    def load_attendance_section_filter(self):
        """Load available sections for filtering"""
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT section FROM students ORDER BY section")
        sections = cur.fetchall()
        conn.close()

        section_values = ["All Sections"] + [section[0] for section in sections]
        self.attendance_section_filter.configure(values=section_values)

    def load_attendance_data(self):
        """Load and display attendance records for selected date"""
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        date_str = self.attendance_date.get()
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
            self.attendance_date.delete(0, "end")
            self.attendance_date.insert(0, date_str)

        section_filter = self.attendance_section_filter.get()

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()

        if section_filter == "All Sections":
            cur.execute("""
                SELECT s.student_id, s.name, s.grade_level, s.section,
                       COALESCE(a.status, 'Not Marked') as status,
                       g.status as academic_status
                FROM students s
                LEFT JOIN attendance a ON s.student_id = a.student_id 
                    AND a.subject = ? AND a.date = ?
                LEFT JOIN grades g ON s.student_id = g.student_id AND g.subject = ?
                WHERE EXISTS (
                    SELECT 1 FROM grades g2 
                    WHERE g2.student_id = s.student_id AND g2.subject = ?
                )
                ORDER BY s.section, s.name
            """, (self.selected_subject, date_str, self.selected_subject, self.selected_subject))
        else:
            cur.execute("""
                SELECT s.student_id, s.name, s.grade_level, s.section,
                       COALESCE(a.status, 'Not Marked') as status,
                       g.status as academic_status
                FROM students s
                LEFT JOIN attendance a ON s.student_id = a.student_id 
                    AND a.subject = ? AND a.date = ?
                LEFT JOIN grades g ON s.student_id = g.student_id AND g.subject = ?
                WHERE EXISTS (
                    SELECT 1 FROM grades g2 
                    WHERE g2.student_id = s.student_id AND g2.subject = ?
                ) AND s.section = ?
                ORDER BY s.name
            """, (
                self.selected_subject, date_str, self.selected_subject,
                self.selected_subject, section_filter
            ))

        rows = cur.fetchall()
        conn.close()

        # Populate treeview with attendance data
        for row in rows:
            attendance_status = row[4]
            academic_status = row[5] if row[5] else "Not Enrolled"
            status_display = "Present" if attendance_status == "P" else \
                "Absent" if attendance_status == "A" else "Not Marked"

            if academic_status == "Dropped":
                status_display = f"Dropped ({status_display})"

            mark_display = "X Absent" if attendance_status == "A" else \
                "Not Marked" if attendance_status == "Not Marked" else "Present"

            self.attendance_tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3],
                status_display,
                mark_display
            ))

    def filter_attendance(self, event=None):
        """Apply section filter to attendance data"""
        self.load_attendance_data()

    def bulk_mark_attendance(self, status):
        """Mark selected students as present or absent"""
        selected = self.attendance_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select students to mark!")
            return

        date_str = self.attendance_date.get()

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()

        for item in selected:
            student_id = self.attendance_tree.item(item)["values"][0]

            # Check if student is dropped
            cur.execute("""
                SELECT status FROM grades 
                WHERE student_id = ? AND subject = ?
            """, (student_id, self.selected_subject))

            academic_status = cur.fetchone()
            if academic_status and academic_status[0] == "Dropped":
                continue

            # Check for existing attendance record
            cur.execute("""
                SELECT id FROM attendance 
                WHERE student_id = ? AND subject = ? AND date = ?
            """, (student_id, self.selected_subject, date_str))

            existing_record = cur.fetchone()

            if existing_record:
                # Update existing record
                cur.execute("""
                    UPDATE attendance SET status = ?
                    WHERE student_id = ? AND subject = ? AND date = ?
                """, (status, student_id, self.selected_subject, date_str))
            else:
                # Insert new record
                cur.execute("""
                    INSERT INTO attendance (student_id, subject, date, status)
                    VALUES (?, ?, ?, ?)
                """, (student_id, self.selected_subject, date_str, status))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            f"Marked {len(selected)} students as {'Present' if status == 'P' else 'Absent'}"
        )

        self.load_attendance_data()

        # Refresh dashboard stats
        if self.selected_subject and self.current_stats_frame:
            self.create_stats_section(self.current_stats_frame)