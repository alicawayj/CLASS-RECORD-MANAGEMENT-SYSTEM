import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3


class GradesTabMixin:
    def setup_grades_tab(self, parent):
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(search_frame, text="Search:", font=("Arial", 14)).pack(side="left", padx=(0, 10))
        self.grade_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search students...",
            width=200
        )
        self.grade_search_entry.pack(side="left", padx=(0, 10))
        self.grade_search_entry.bind("<KeyRelease>", self.search_grades)

        ctk.CTkLabel(search_frame, text="Filter:", font=("Arial", 14)).pack(side="left", padx=(10, 10))
        self.grade_filter = ctk.CTkComboBox(
            search_frame,
            values=["All", "Passing", "Failing", "Dropped"],
            width=120
        )
        self.grade_filter.set("All")
        self.grade_filter.pack(side="left", padx=(0, 10))
        self.grade_filter.bind("<<ComboboxSelected>>", self.filter_grades)

        ctk.CTkLabel(search_frame, text="Section:", font=("Arial", 14)).pack(side="left", padx=(10, 10))
        self.section_filter = ctk.CTkComboBox(
            search_frame,
            values=["All Sections"],
            width=150
        )
        self.section_filter.set("All Sections")
        self.section_filter.pack(side="left", padx=(0, 10))

        confirm_filter_btn = ctk.CTkButton(
            search_frame,
            text="Apply Section Filter",
            command=self.confirm_section_filter,
            width=150,
            height=30,
            fg_color="#2E8B57",
            hover_color="#1F5E3A"
        )
        confirm_filter_btn.pack(side="left", padx=(10, 0))

        refresh_btn = ctk.CTkButton(
            search_frame,
            text="Refresh",
            command=self.load_section_filter,
            width=80,
            height=30
        )
        refresh_btn.pack(side="left", padx=(10, 0))

        delete_student_btn = ctk.CTkButton(
            search_frame,
            text="🗑️ Move to Trash Bin",
            command=self.delete_student_from_subject,
            width=180,
            height=30,
            fg_color="#DC143C",
            hover_color="#B22222"
        )
        delete_student_btn.pack(side="left", padx=(10, 0))

        self.load_section_filter()

        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill="both", expand=True, pady=10)

        tree_container = ctk.CTkFrame(table_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        columns = (
            "ID", "Name", "Grade Level", "Section",
            "Written Works", "Quizzes", "Activities",
            "Performance Tasks", "Final Grade", "Status"
        )
        self.grades_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=12)

        column_config = {
            "ID": 80,
            "Name": 150,
            "Grade Level": 80,
            "Section": 120,
            "Written Works": 100,
            "Quizzes": 80,
            "Activities": 90,
            "Performance Tasks": 120,
            "Final Grade": 90,
            "Status": 80
        }

        for col in columns:
            self.grades_tree.heading(col, text=col)
            self.grades_tree.column(col, width=column_config[col])

        self.grades_tree.tag_configure('passing', background='#d4edda', foreground='#155724')
        self.grades_tree.tag_configure('failing', background='#f8d7da', foreground='#721c24')
        self.grades_tree.tag_configure('dropped', background='#f5e6e8', foreground='#721c24', font=('Arial', 10, 'italic'))

        scrollbar_x = ttk.Scrollbar(tree_container, orient="horizontal", command=self.grades_tree.xview)
        scrollbar_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.grades_tree.yview)
        self.grades_tree.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

        self.grades_tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#2a2d2e",
            foreground="white",
            fieldbackground="#2a2d2e",
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background="#3b3b3b",
            foreground="white",
            relief="flat"
        )
        style.map('Treeview', background=[('selected', '#22559b')])

        self.load_grades_data_with_filters()

    def delete_student_from_subject(self):
        """Delete student from subject and move to trash bin"""
        selected = self.grades_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to delete!")
            return

        student_id = self.grades_tree.item(selected[0])["values"][0]
        student_name = self.grades_tree.item(selected[0])["values"][1]
        subject = self.selected_subject

        result = messagebox.askyesno(
            "Confirm Move to Trash",
            f"Are you sure you want to move {student_name} to trash bin?\n" +
            f"This will remove them from {subject}.\n" +
            "You can restore them later from the Trash Bin tab."
        )

        if not result:
            return

        # Use the move_student_to_trash method from ManagementMixin
        try:
            self.move_student_to_trash(student_id, student_name, subject)
            messagebox.showinfo(
                "Success",
                f"Student {student_name} moved to trash bin!\n" +
                f"They have been removed from {subject}."
            )
            
            self.load_grades_data_with_filters()
            if hasattr(self, 'refresh_dashboard_stats'):
                self.refresh_dashboard_stats()
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to move student to trash: {str(e)}")

    def confirm_section_filter(self):
        self.load_grades_data_with_filters()
        messagebox.showinfo(
            "Filter Applied",
            f"Now showing students from: {self.section_filter.get()}"
        )

    def load_section_filter(self):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT section FROM students ORDER BY section")
        sections = cur.fetchall()
        conn.close()

        section_values = ["All Sections"] + [section[0] for section in sections]
        self.section_filter.configure(values=section_values)

    def load_grades_data_with_filters(self):
        for item in self.grades_tree.get_children():
            self.grades_tree.delete(item)

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()

        query = """
            SELECT s.student_id, s.name, s.grade_level, s.section, 
                   g.written_works, g.quizzes, g.activities, g.performance_tasks, 
                   g.final_grade, g.status 
            FROM students s
            JOIN grades g ON s.student_id = g.student_id
            WHERE g.subject = ?
        """

        params = [self.selected_subject]

        section_filter = self.section_filter.get()
        if section_filter != "All Sections":
            query += " AND s.section = ?"
            params.append(section_filter)

        status_filter = self.grade_filter.get()
        if status_filter != "All":
            query += " AND g.status = ?"
            params.append(status_filter)

        search_term = self.grade_search_entry.get().strip()
        if search_term:
            query += " AND (s.name LIKE ? OR s.student_id LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])

        query += " ORDER BY s.section, s.name"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            status = row[9]
            tag = ''
            if status == 'Passing':
                tag = 'passing'
            elif status == 'Failing':
                tag = 'failing'
            elif status == 'Dropped':
                tag = 'dropped'

            self.grades_tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3],
                f"{row[4]:.1f}%" if row[4] is not None else "N/A",
                f"{row[5]:.1f}%" if row[5] is not None else "N/A",
                f"{row[6]:.1f}%" if row[6] is not None else "N/A",
                f"{row[7]:.1f}%" if row[7] is not None else "N/A",
                f"{row[8]:.1f}%" if row[8] is not None else "N/A",
                status
            ), tags=(tag,))

    def search_grades(self, event=None):
        self.load_grades_data_with_filters()

    def filter_grades(self, event=None):
        self.load_grades_data_with_filters()