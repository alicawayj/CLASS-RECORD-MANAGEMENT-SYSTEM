import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime

class SubjectDashboard:
    def __init__(self, main_content, subject, backend, refresh_stats_callback):
        self.main_content = main_content
        self.subject = subject
        self.backend = backend
        self.refresh_stats_callback = refresh_stats_callback
        self.setup_ui()

    def setup_ui(self):
        self.clear_main_content()
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header_frame, text=f"📚 {self.subject} - Student Records", font=("Arial", 28, "bold")).pack(anchor="w")
        self.current_stats_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.current_stats_frame.pack(fill="x", pady=(0, 20))
        self.create_stats_section()
        tabview = ctk.CTkTabview(self.main_content)
        tabview.pack(fill="both", expand=True, pady=10)
        tabview.add("Grades")
        tabview.add("Attendance")
        tabview.add("Update Records")
        self.setup_grades_tab(tabview.tab("Grades"))
        self.setup_attendance_tab(tabview.tab("Attendance"))
        self.setup_update_tab(tabview.tab("Update Records"))

    def create_stats_section(self):
        total, avg_grade, failing, absences = self.backend.get_subject_stats(self.subject)
        stats_data = [
            ("Students", total, "#2E8B57"),
            ("Avg Grade", f"{avg_grade:.1f}%" if avg_grade else "0.0%", "#4169E1"),
            ("Failing", failing, "#DC143C"),
            ("Absences", absences, "#FF8C00")
        ]
        for i, (title, value, color) in enumerate(stats_data):
            card = ctk.CTkFrame(self.current_stats_frame, width=160, height=80, border_color=color, border_width=2, corner_radius=8)
            card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=title, font=("Arial", 11, "bold"), wraplength=140).pack(pady=(8, 2))
            ctk.CTkLabel(card, text=str(value), font=("Arial", 18, "bold"), text_color=color).pack(pady=(2, 8))
        self.current_stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def setup_grades_tab(self, parent):
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(search_frame, text="🔍 Search:", font=("Arial", 14)).pack(side="left", padx=(0, 10))
        self.grade_search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search students...", width=200)
        self.grade_search_entry.pack(side="left", padx=(0, 10))
        self.grade_search_entry.bind("<KeyRelease>", self.search_grades)
        ctk.CTkLabel(search_frame, text="Filter:", font=("Arial", 14)).pack(side="left", padx=(10, 10))
        self.grade_filter = ctk.CTkComboBox(search_frame, values=["All", "Passing", "Failing"], width=120)
        self.grade_filter.set("All")
        self.grade_filter.pack(side="left", padx=(0, 10))
        self.grade_filter.bind("<<ComboboxSelected>>", self.filter_grades)
        ctk.CTkLabel(search_frame, text="Section:", font=("Arial", 14)).pack(side="left", padx=(10, 10))
        self.section_filter = ctk.CTkComboBox(search_frame, values=["All Sections"], width=150)
        self.section_filter.set("All Sections")
        self.section_filter.pack(side="left", padx=(0, 10))
        confirm_filter_btn = ctk.CTkButton(search_frame, text="✅ Apply Section Filter", command=self.confirm_section_filter, width=150, height=30, fg_color="#2E8B57", hover_color="#1F5E3A")
        confirm_filter_btn.pack(side="left", padx=(10, 0))
        refresh_btn = ctk.CTkButton(search_frame, text="🔄 Refresh", command=self.load_section_filter, width=80, height=30)
        refresh_btn.pack(side="left", padx=(10, 0))
        self.load_section_filter()
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill="both", expand=True, pady=10)
        tree_container = ctk.CTkFrame(table_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ("ID", "Name", "Grade Level", "Section", "Written Works", "Quizzes", "Activities", "Performance Tasks", "Final Grade", "Status")
        self.grades_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=12)
        column_config = {
            "ID": 80, "Name": 150, "Grade Level": 80, "Section": 120,
            "Written Works": 100, "Quizzes": 80, "Activities": 90,
            "Performance Tasks": 120, "Final Grade": 90, "Status": 80
        }
        for col in columns:
            self.grades_tree.heading(col, text=col)
            self.grades_tree.column(col, width=column_config[col])
        scrollbar_x = ttk.Scrollbar(tree_container, orient="horizontal", command=self.grades_tree.xview)
        scrollbar_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.grades_tree.yview)
        self.grades_tree.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)
        self.grades_tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#2a2d2e", borderwidth=0)
        style.configure("Treeview.Heading", background="#3b3b3b", foreground="white", relief="flat")
        style.map('Treeview', background=[('selected', '#22559b')])
        self.load_grades_data_with_filters()

    def load_section_filter(self):
        sections = self.backend.get_sections()
        section_values = ["All Sections"] + sections
        self.section_filter.configure(values=section_values)

    def confirm_section_filter(self):
        self.load_grades_data_with_filters()
        messagebox.showinfo("Filter Applied", f"Now showing students from: {self.section_filter.get()}")

    def load_grades_data_with_filters(self):
        for item in self.grades_tree.get_children():
            self.grades_tree.delete(item)
        section_filter = self.section_filter.get()
        status_filter = self.grade_filter.get()
        search_term = self.grade_search_entry.get().strip()
        rows = self.backend.get_grades_data(self.subject, section_filter, status_filter, search_term)
        for row in rows:
            status_icon = "✅" if row[9] == "Passing" else "❌"
            self.grades_tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3],
                f"{row[4]:.1f}%" if row[4] is not None else "N/A",
                f"{row[5]:.1f}%" if row[5] is not None else "N/A",
                f"{row[6]:.1f}%" if row[6] is not None else "N/A",
                f"{row[7]:.1f}%" if row[7] is not None else "N/A",
                f"{row[8]:.1f}%" if row[8] is not None else "N/A",
                f"{status_icon} {row[9]}"
            ))

    def search_grades(self, event=None):
        self.load_grades_data_with_filters()

    def filter_grades(self, event=None):
        self.load_grades_data_with_filters()

    def setup_attendance_tab(self, parent):
        date_frame = ctk.CTkFrame(parent, fg_color="transparent")
        date_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(date_frame, text="Select Date:", font=("Arial", 14)).pack(side="left", padx=(0, 10))
        self.attendance_date = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD", width=150)
        self.attendance_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.attendance_date.pack(side="left", padx=(0, 10))
        ctk.CTkButton(date_frame, text="Load Attendance", command=self.load_attendance_data, width=150, height=35).pack(side="left", padx=(0, 10))
        ctk.CTkButton(date_frame, text="🔄 Refresh Stats", command=self.refresh_dashboard_stats, width=120, height=35, fg_color="#4169E1").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(date_frame, text="Section:", font=("Arial", 14)).pack(side="left", padx=(10, 10))
        self.attendance_section_filter = ctk.CTkComboBox(date_frame, values=["All Sections"], width=150)
        self.attendance_section_filter.set("All Sections")
        self.attendance_section_filter.pack(side="left", padx=(0, 10))
        self.attendance_section_filter.bind("<<ComboboxSelected>>", self.filter_attendance)
        self.load_attendance_section_filter()
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill="both", expand=True, pady=10)
        tree_container = ctk.CTkFrame(table_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ("ID", "Name", "Grade Level", "Section", "Status", "Mark")
        self.attendance_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)
        column_config = {
            "ID": 80, "Name": 200, "Grade Level": 100,
            "Section": 120, "Status": 120, "Mark": 80
        }
        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=column_config[col])
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)
        self.attendance_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        ctk.CTkButton(button_frame, text="Mark Selected as Present (P)", command=lambda: self.bulk_mark_attendance("P"), fg_color="#2E8B57", hover_color="#1F5E3A", height=40).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Mark Selected as Absent (A)", command=lambda: self.bulk_mark_attendance("A"), fg_color="#DC143C", hover_color="#B22222", height=40).pack(side="left", padx=5)
        self.load_attendance_data()

    def load_attendance_section_filter(self):
        sections = self.backend.get_sections()
        section_values = ["All Sections"] + sections
        self.attendance_section_filter.configure(values=section_values)

    def load_attendance_data(self):
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        date_str = self.attendance_date.get()
        section_filter = self.attendance_section_filter.get()
        rows = self.backend.get_attendance_data(self.subject, date_str, section_filter)
        for row in rows:
            status = row[4]
            status_display = "✅ Present" if status == "P" else "❌ Absent" if status == "A" else "⏳ Not Marked"
            mark_display = "X Absent" if status == "A" else "Not Marked" if status == "Not Marked" else "Present"
            self.attendance_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], status_display, mark_display))

    def filter_attendance(self, event=None):
        self.load_attendance_data()

    def bulk_mark_attendance(self, status):
        selected = self.attendance_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select students to mark!")
            return
        date_str = self.attendance_date.get()
        for item in selected:
            student_id = self.attendance_tree.item(item)["values"][0]
            self.backend.update_attendance(student_id, self.subject, date_str, status)
        messagebox.showinfo("Success", f"Marked {len(selected)} students as {'Present' if status == 'P' else 'Absent'}")
        self.load_attendance_data()
        self.refresh_dashboard_stats()

    def refresh_dashboard_stats(self):
        self.refresh_stats_callback()

    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()