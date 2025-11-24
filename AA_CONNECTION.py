import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime, timedelta
import random

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class Teacher:
    def __init__(self, teacher_id, name, email, subjects):
        self.teacher_id = teacher_id
        self.name = name
        self.email = email
        self.subjects = subjects

class Student:
    def __init__(self, student_id, name, grade_level, section, subjects):
        self.student_id = student_id
        self.name = name
        self.grade_level = grade_level
        self.section = section
        self.subjects = subjects
        self.attendance = {}

class ClassRecordSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Class Record Management System")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        self.center_window(1400, 900)
        
        self.current_user = None
        self.selected_subject = None
        self.current_attendance_section = "All Sections"
        self.current_stats_frame = None
        
        self.db_setup()
        self.generate_sample_data()
        self.login_screen()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def db_setup(self):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                subjects TEXT
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT,
                grade_level INTEGER,
                section TEXT,
                subjects TEXT,
                attendance TEXT
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                subject TEXT,
                written_works REAL,
                quizzes REAL,
                activities REAL,
                performance_tasks REAL,
                final_grade REAL,
                status TEXT,
                timestamp TEXT
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                subject TEXT,
                date TEXT,
                status TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT UNIQUE,
                teacher_id TEXT
            )
        """)
        conn.commit()
        conn.close()

    def generate_sample_data(self):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM teachers")
        if cur.fetchone()[0] == 0:
            teachers = [
                ("T001", "Dr. Sarah Johnson", "s.johnson@school.edu", "Math,Physics"),
                ("T002", "Prof. Michael Chen", "m.chen@school.edu", "Science,Biology"),
                ("T003", "Ms. Emily Davis", "e.davis@school.edu", "English,Literature"),
                ("T004", "Mr. Robert Wilson", "r.wilson@school.edu", "History,Geography")
            ]
            for teacher in teachers:
                cur.execute("INSERT INTO teachers VALUES (?, ?, ?, ?)", teacher)
            
            all_subjects = ["Math", "Science", "English", "History", "Physics", "Biology", "Literature", "Geography"]
            for subject in all_subjects:
                try:
                    cur.execute("INSERT INTO subjects (subject_name) VALUES (?)", (subject,))
                except sqlite3.IntegrityError:
                    pass
            
            first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
            
            sections = ["Diamond", "Ruby", "Emerald", "Sapphire", "Pearl"]
            grade_levels = [9, 10, 11, 12]
            
            student_count = 0
            for grade_level in grade_levels:
                for section in sections:
                    for i in range(5):
                        student_count += 1
                        student_id = f"S{student_count:03d}"
                        first_name = random.choice(first_names)
                        last_name = random.choice(last_names)
                        name = f"{first_name} {last_name}"
                        section_name = f"Grade {grade_level} {section}"
                        
                        student_subjects = {}
                        num_subjects = random.randint(3, 6)
                        selected_subjects = random.sample(all_subjects, num_subjects)
                        
                        for subject in selected_subjects:
                            written_works = round(random.uniform(80.0, 95.0), 1)
                            quizzes = round(random.uniform(75.0, 92.0), 1)
                            activities = round(random.uniform(85.0, 98.0), 1)
                            performance_tasks = round(random.uniform(82.0, 96.0), 1)
                            
                            final_grade = (written_works * 0.25 + quizzes * 0.25 + 
                                         activities * 0.25 + performance_tasks * 0.25)
                            
                            student_subjects[subject] = {
                                'written_works': written_works,
                                'quizzes': quizzes,
                                'activities': activities,
                                'performance_tasks': performance_tasks,
                                'final_grade': round(final_grade, 1)
                            }
                    
                        attendance_data = {}
                        for day in range(1, 16):
                            date_str = f"2024-01-{day:02d}"
                            attendance_data[date_str] = "P" if random.random() < 0.85 else "A"
                        
                        cur.execute(
                            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)",
                            (student_id, name, grade_level, section_name, str(student_subjects), str(attendance_data))
                        )
                        
                        for subject, grades in student_subjects.items():
                            status = "Passing" if grades['final_grade'] >= 75.0 else "Failing"
                            cur.execute(
                                """INSERT INTO grades 
                                (student_id, subject, written_works, quizzes, activities, performance_tasks, final_grade, status, timestamp) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (student_id, subject, grades['written_works'], grades['quizzes'], 
                                 grades['activities'], grades['performance_tasks'], grades['final_grade'], 
                                 status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            )
                        
                        for subject in selected_subjects:
                            for date_str, status in attendance_data.items():
                                cur.execute(
                                    "INSERT INTO attendance (student_id, subject, date, status) VALUES (?, ?, ?, ?)",
                                    (student_id, subject, date_str, status)
                                )
        
        conn.commit()
        conn.close()

    def login_screen(self):
        self.clear_window()

        main_container = ctk.CTkFrame(self.root, fg_color=("gray95", "gray15"))
        main_container.pack(fill="both", expand=True)

        left_frame = ctk.CTkFrame(main_container, fg_color=("#2E8B57", "#1F5E3A"), width=400)
        left_frame.pack(side="left", fill="both", expand=False)
        left_frame.pack_propagate(False)

        brand_content = ctk.CTkFrame(left_frame, fg_color="transparent")
        brand_content.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            brand_content, 
            text="🎓", 
            font=("Arial", 64),
            text_color="white"
        ).pack(pady=10)

        ctk.CTkLabel(
            brand_content,
            text="CLASS RECORD",
            font=("Arial", 28, "bold"),
            text_color="white"
        ).pack(pady=5)

        ctk.CTkLabel(
            brand_content,
            text="Management System",
            font=("Arial", 16),
            text_color="white"
        ).pack(pady=5)

        right_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True, padx=80)

        form_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        form_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            form_frame,
            text="Good Day!, Sir Meo, Sir Yno, Sir Harold",
            font=("Arial", 24, "bold"),
            text_color="#2E8B57"
        ).pack(pady=20)

        ctk.CTkLabel(
            form_frame,
            text="Teacher Login Portal",
            font=("Arial", 18),
            text_color=("gray50", "gray70")
        ).pack(pady=5)

        ctk.CTkLabel(form_frame, text="Teacher ID", font=("Arial", 14)).pack(anchor="w", pady=(20, 5))
        self.teacher_id_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your teacher ID",
            width=300,
            height=45,
            font=("Arial", 14)
        )
        self.teacher_id_entry.pack(pady=5)
        self.teacher_id_entry.insert(0, "T001")

        ctk.CTkLabel(form_frame, text="Name", font=("Arial", 14)).pack(anchor="w", pady=(20, 5))
        self.teacher_name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your full name",
            width=300,
            height=45,
            font=("Arial", 14)
        )
        self.teacher_name_entry.pack(pady=5)
        self.teacher_name_entry.insert(0, "Dr. Sarah Johnson")

        login_btn = ctk.CTkButton(
            form_frame,
            text="Sign In →",
            command=self.check_login,
            width=300,
            height=45,
            font=("Arial", 16, "bold"),
            fg_color=("#2E8B57", "#1F5E3A"),
            hover_color=("#1F5E3A", "#2E8B57"),
            corner_radius=8
        )
        login_btn.pack(pady=30)

        self.root.bind('<Return>', lambda event: self.check_login())

    def check_login(self):
        teacher_id = self.teacher_id_entry.get()
        name = self.teacher_name_entry.get()

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM teachers WHERE teacher_id = ? AND name = ?", (teacher_id, name))
        teacher = cur.fetchone()
        conn.close()

        if teacher:
            self.current_user = teacher
            self.main_screen()
        else:
            messagebox.showerror("Login Error", "Invalid teacher ID or name.")

    def main_screen(self):
        self.clear_window()

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

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

        nav_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15)

        ctk.CTkLabel(
            nav_frame, 
            text="SUBJECTS", 
            font=("Arial", 12, "bold"),
            text_color=("gray50", "gray70")
        ).pack(anchor="w", pady=(10, 5))

        subjects = self.current_user[3].split(",")
        for subject in subjects:
            subject_btn = ctk.CTkButton(
                nav_frame,
                text=f"📚 {subject}",
                command=lambda subj=subject: self.show_subject_dashboard(subj),
                fg_color="transparent",
                hover_color=("gray80", "gray30"),
                anchor="w",
                height=40
            )
            subject_btn.pack(fill="x", pady=2)

        ctk.CTkLabel(
            nav_frame,
            text="MANAGEMENT",
            font=("Arial", 12, "bold"),
            text_color=("gray50", "gray70")
        ).pack(anchor="w", pady=(20, 5))

        manage_subjects_btn = ctk.CTkButton(
            nav_frame,
            text="📋 Manage Subjects",
            command=self.manage_subjects,
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            anchor="w",
            height=40
        )
        manage_subjects_btn.pack(fill="x", pady=2)

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

        self.main_content = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.show_welcome_screen()

    def show_welcome_screen(self):
        self.clear_main_content()

        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header_frame,
            text="👋 Welcome Back!",
            font=("Arial", 28, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Select a subject from the sidebar to manage student records",
            font=("Arial", 16),
            text_color=("gray50", "gray70")
        ).pack(anchor="w", pady=(5, 0))

        stats_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(DISTINCT student_id) FROM students")
        total_students = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM grades WHERE status = 'Failing'")
        failing_students = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM attendance WHERE status = 'A'")
        total_absences = cur.fetchone()[0]
        
        conn.close()

        stats_data = [
            ("Students", total_students, "#2E8B57"),
            ("Failing", failing_students, "#DC143C"),
            ("Absences", total_absences, "#FF8C00"),
            ("Subjects", len(self.current_user[3].split(",")), "#4169E1")
        ]

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

        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def show_subject_dashboard(self, subject):
        self.selected_subject = subject
        self.clear_main_content()

        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header_frame,
            text=f"📚 {subject} - Student Records",
            font=("Arial", 28, "bold")
        ).pack(anchor="w")

        self.current_stats_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.current_stats_frame.pack(fill="x", pady=(0, 20))

        self.create_stats_section(self.current_stats_frame)
        
        tabview = ctk.CTkTabview(self.main_content)
        tabview.pack(fill="both", expand=True, pady=10)
        
        tabview.add("Grades")
        tabview.add("Attendance")
        tabview.add("Update Records")

        self.setup_grades_tab(tabview.tab("Grades"))
        self.setup_attendance_tab(tabview.tab("Attendance"))
        self.setup_update_tab(tabview.tab("Update Records"))

    def create_stats_section(self, stats_frame):
        for widget in stats_frame.winfo_children():
            widget.destroy()

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*), AVG(final_grade), 
                   SUM(CASE WHEN status = 'Failing' THEN 1 ELSE 0 END)
            FROM grades WHERE subject = ?
        """, (self.selected_subject,))
        result = cur.fetchone()
        total = result[0] if result else 0
        avg_grade = result[1] if result and result[1] else 0
        failing = result[2] if result else 0
        
        # COUNT ABSENCES - FIXED QUERY
        cur.execute("""
            SELECT COUNT(*) 
            FROM attendance 
            WHERE subject = ? AND status = 'A'
        """, (self.selected_subject,))
        result = cur.fetchone()
        absences = result[0] if result else 0
        
        conn.close()

        stats_data = [
            ("Students", total, "#2E8B57"),
            ("Avg Grade", f"{avg_grade:.1f}%" if avg_grade else "0.0%", "#4169E1"),
            ("Failing", failing, "#DC143C"),
            ("Absences", absences, "#FF8C00")
        ]

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

        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def refresh_dashboard_stats(self):
        if self.selected_subject and self.current_stats_frame:
            self.create_stats_section(self.current_stats_frame)

    def setup_grades_tab(self, parent):
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(search_frame, text="🔍 Search:", font=("Arial", 14)).pack(side="left", padx=(0, 10))
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
            values=["All", "Passing", "Failing"],
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

        # ADDED: Confirm Filter Button
        confirm_filter_btn = ctk.CTkButton(
            search_frame,
            text="✅ Apply Section Filter",
            command=self.confirm_section_filter,
            width=150,
            height=30,
            fg_color="#2E8B57",
            hover_color="#1F5E3A"
        )
        confirm_filter_btn.pack(side="left", padx=(10, 0))

        # Refresh button for sections
        refresh_btn = ctk.CTkButton(
            search_frame,
            text="🔄 Refresh",
            command=self.load_section_filter,
            width=80,
            height=30
        )
        refresh_btn.pack(side="left", padx=(10, 0))

        self.load_section_filter()

        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill="both", expand=True, pady=10)

        tree_container = ctk.CTkFrame(table_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Name", "Grade Level", "Section", "Written Works", "Quizzes", "Activities", "Performance Tasks", "Final Grade", "Status")
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

        scrollbar_x = ttk.Scrollbar(tree_container, orient="horizontal", command=self.grades_tree.xview)
        scrollbar_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.grades_tree.yview)
        self.grades_tree.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

        self.grades_tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                       background="#2a2d2e",
                       foreground="white",
                       fieldbackground="#2a2d2e",
                       borderwidth=0)
        style.configure("Treeview.Heading", 
                       background="#3b3b3b", 
                       foreground="white",
                       relief="flat")
        style.map('Treeview', background=[('selected', '#22559b')])

        self.load_grades_data_with_filters()

    def confirm_section_filter(self):
        """Apply the selected section filter"""
        self.load_grades_data_with_filters()
        messagebox.showinfo("Filter Applied", f"Now showing students from: {self.section_filter.get()}")

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
        
        # Build the query with filters
        query = """
            SELECT s.student_id, s.name, s.grade_level, s.section, 
                   g.written_works, g.quizzes, g.activities, g.performance_tasks, 
                   g.final_grade, g.status 
            FROM students s
            JOIN grades g ON s.student_id = g.student_id
            WHERE g.subject = ?
        """
        
        params = [self.selected_subject]
        
        # Add section filter if not "All Sections"
        section_filter = self.section_filter.get()
        if section_filter != "All Sections":
            query += " AND s.section = ?"
            params.append(section_filter)
        
        # Add status filter if not "All"
        status_filter = self.grade_filter.get()
        if status_filter != "All":
            if status_filter == "Passing":
                query += " AND g.status = 'Passing'"
            elif status_filter == "Failing":
                query += " AND g.status = 'Failing'"
        
        # Add search filter if there's a search term
        search_term = self.grade_search_entry.get().strip()
        if search_term:
            query += " AND (s.name LIKE ? OR s.student_id LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        query += " ORDER BY s.section, s.name"
        
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

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
        
        self.attendance_date = ctk.CTkEntry(
            date_frame,
            placeholder_text="YYYY-MM-DD",
            width=150
        )
        self.attendance_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
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
            text="🔄 Refresh Stats",
            command=self.refresh_dashboard_stats,
            width=120,
            height=35,
            fg_color="#4169E1"
        ).pack(side="left", padx=(0, 10))

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
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT section FROM students ORDER BY section")
        sections = cur.fetchall()
        conn.close()
        
        section_values = ["All Sections"] + [section[0] for section in sections]
        self.attendance_section_filter.configure(values=section_values)

    def load_attendance_data(self):
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
            
        date_str = self.attendance_date.get()
        section_filter = self.attendance_section_filter.get()
        
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        
        if section_filter == "All Sections":
            cur.execute("""
                SELECT s.student_id, s.name, s.grade_level, s.section,
                       COALESCE(a.status, 'Not Marked') as status
                FROM students s
                LEFT JOIN attendance a ON s.student_id = a.student_id 
                    AND a.subject = ? AND a.date = ?
                WHERE EXISTS (
                    SELECT 1 FROM grades g 
                    WHERE g.student_id = s.student_id AND g.subject = ?
                )
                ORDER BY s.section, s.name
            """, (self.selected_subject, date_str, self.selected_subject))
        else:
            cur.execute("""
                SELECT s.student_id, s.name, s.grade_level, s.section,
                       COALESCE(a.status, 'Not Marked') as status
                FROM students s
                LEFT JOIN attendance a ON s.student_id = a.student_id 
                    AND a.subject = ? AND a.date = ?
                WHERE EXISTS (
                    SELECT 1 FROM grades g 
                    WHERE g.student_id = s.student_id AND g.subject = ?
                ) AND s.section = ?
                ORDER BY s.name
            """, (self.selected_subject, date_str, self.selected_subject, section_filter))
            
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            status = row[4]
            status_display = "✅ Present" if status == "P" else "❌ Absent" if status == "A" else "⏳ Not Marked"
            mark_display = "X Absent" if status == "A" else "Not Marked" if status == "Not Marked" else "Present"
            
            self.attendance_tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3], 
                status_display, 
                mark_display
            ))

    def filter_attendance(self, event=None):
        self.load_attendance_data()

    def bulk_mark_attendance(self, status):
        selected = self.attendance_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select students to mark!")
            return

        date_str = self.attendance_date.get()
        
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        
        for item in selected:
            student_id = self.attendance_tree.item(item)["values"][0]
            
            # Check if attendance record already exists
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
        
        messagebox.showinfo("Success", f"Marked {len(selected)} students as {'Present' if status == 'P' else 'Absent'}")
        
        # Refresh the attendance display
        self.load_attendance_data()
        
        # Force refresh the stats
        if self.selected_subject and self.current_stats_frame:
            self.create_stats_section(self.current_stats_frame)

    def setup_update_tab(self, parent):
        # Create a scrollable frame for the update tab
        main_scrollable = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        main_scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main form container
        form_frame = ctk.CTkFrame(main_scrollable, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(
            form_frame,
            text="Update Student Grades",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=(0, 20))

        # Student Selection Section
        selection_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        selection_frame.pack(fill="x", pady=(10, 20))
        
        ctk.CTkLabel(selection_frame, text="Select Student:", font=("Arial", 14)).pack(anchor="w", pady=(10, 5))
        
        student_controls_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        student_controls_frame.pack(fill="x", pady=5)
        
        self.student_combobox = ctk.CTkComboBox(
            student_controls_frame,
            width=400,
            height=40,
            dropdown_font=("Arial", 12)
        )
        self.student_combobox.pack(side="left", padx=(0, 10))
        self.load_student_combobox()
        
        ctk.CTkButton(
            student_controls_frame,
            text="Load Student",
            command=self.load_student_data,
            width=120,
            height=40,
            fg_color="#4169E1"
        ).pack(side="left")

        # Current Grades Display - Make this section more compact
        current_grades_frame = ctk.CTkFrame(form_frame, corner_radius=10)
        current_grades_frame.pack(fill="x", pady=15, padx=5)

        ctk.CTkLabel(
            current_grades_frame,
            text="Current Grades:",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=(12, 8), padx=12)

        # Use a grid layout for current grades
        grades_grid = ctk.CTkFrame(current_grades_frame, fg_color="transparent")
        grades_grid.pack(fill="x", padx=12, pady=8)

        self.current_grades_labels = {}
        grade_components = ["Written Works", "Quizzes", "Activities", "Performance Tasks", "Final Grade", "Status"]
        
        # Create 2 rows with 3 columns each
        for i, component in enumerate(grade_components):
            row = i // 3
            col = i % 3
            
            comp_frame = ctk.CTkFrame(grades_grid, fg_color="transparent")
            comp_frame.grid(row=row, column=col, padx=10, pady=8, sticky="w")
            
            ctk.CTkLabel(
                comp_frame, 
                text=f"{component}:", 
                font=("Arial", 12, "bold")
            ).pack(anchor="w")
            
            label = ctk.CTkLabel(
                comp_frame,
                text="N/A",
                font=("Arial", 13, "bold"),
                text_color="#2E8B57"
            )
            label.pack(anchor="w", pady=(3, 0))
            self.current_grades_labels[component.lower().replace(" ", "_")] = label

        # Configure grid weights for even spacing
        for i in range(3):
            grades_grid.columnconfigure(i, weight=1)

        # Update Grades Section - Make this more compact
        update_frame = ctk.CTkFrame(form_frame, corner_radius=10)
        update_frame.pack(fill="x", pady=15, padx=5)

        ctk.CTkLabel(
            update_frame,
            text="Update Grades:",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=(12, 8), padx=12)

        update_grid = ctk.CTkFrame(update_frame, fg_color="transparent")
        update_grid.pack(fill="x", padx=12, pady=8)

        self.grade_entries = {}
        update_components = [
            ("Written Works", "written_works"),
            ("Quizzes", "quizzes"), 
            ("Activities", "activities"),
            ("Performance Tasks", "performance_tasks")
        ]
        
        # Create 2x2 grid for update inputs
        for i, (display_name, field_name) in enumerate(update_components):
            row = i // 2
            col = (i % 2)
            
            comp_frame = ctk.CTkFrame(update_grid, fg_color="transparent")
            comp_frame.grid(row=row, column=col, padx=15, pady=10, sticky="w")
            
            ctk.CTkLabel(
                comp_frame, 
                text=f"{display_name}:", 
                font=("Arial", 12)
            ).pack(anchor="w")
            
            entry = ctk.CTkEntry(
                comp_frame,
                placeholder_text=f"Enter grade (0-100)",
                width=200,
                height=35,
                font=("Arial", 12)
            )
            entry.pack(anchor="w", pady=5)
            self.grade_entries[field_name] = entry

        # Configure update grid columns
        for i in range(2):
            update_grid.columnconfigure(i, weight=1)

        # Action Buttons - Make them more visible
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=25)

        ctk.CTkButton(
            button_frame,
            text="💾 Update All Grades",
            command=self.update_student_grades,
            fg_color="#2E8B57",
            hover_color="#1F5E3A",
            width=200,
            height=45,
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="🔄 Refresh Data",
            command=self.load_student_data,
            width=150,
            height=45,
            font=("Arial", 14),
            fg_color="#4169E1"
        ).pack(side="left", padx=10)

        # Load initial student data
        self.load_student_data()

    def load_student_combobox(self):
        if not self.selected_subject:
            return
            
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT s.student_id, s.name, s.section
            FROM students s
            JOIN grades g ON s.student_id = g.student_id
            WHERE g.subject = ?
            ORDER BY s.section, s.name
        """, (self.selected_subject,))
        students = cur.fetchall()
        conn.close()
        
        student_list = [f"{student[0]} - {student[1]} ({student[2]})" for student in students]
        self.student_combobox.configure(values=student_list)
        if student_list:
            self.student_combobox.set(student_list[0])

    def load_student_data(self):
        if not self.selected_subject:
            return
            
        selected = self.student_combobox.get()
        if not selected:
            return
            
        student_id = selected.split(" - ")[0]
        
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT written_works, quizzes, activities, performance_tasks, final_grade, status 
            FROM grades 
            WHERE student_id = ? AND subject = ?
        """, (student_id, self.selected_subject))
        result = cur.fetchone()
        conn.close()
        
        if result:
            grades_data = {
                "written_works": f"{result[0]:.1f}%" if result[0] is not None else "N/A",
                "quizzes": f"{result[1]:.1f}%" if result[1] is not None else "N/A",
                "activities": f"{result[2]:.1f}%" if result[2] is not None else "N/A",
                "performance_tasks": f"{result[3]:.1f}%" if result[3] is not None else "N/A",
                "final_grade": f"{result[4]:.1f}%" if result[4] is not None else "N/A",
                "status": result[5] if result[5] else "N/A"
            }
            
            for component, value in grades_data.items():
                if component in self.current_grades_labels:
                    self.current_grades_labels[component].configure(text=value)
                    
            # Clear the entry fields
            for entry in self.grade_entries.values():
                entry.delete(0, "end")

    def update_student_grades(self):
        selected = self.student_combobox.get()
        if not selected:
            messagebox.showerror("Error", "Please select a student!")
            return
            
        student_id = selected.split(" - ")[0]
        
        grades = {}
        total_weight = 0
        valid_components = 0
        
        for component, entry in self.grade_entries.items():
            grade_text = entry.get()
            if grade_text.strip():
                try:
                    grade = float(grade_text)
                    if not (0 <= grade <= 100):
                        raise ValueError("Grade must be between 0 and 100")
                    grades[component] = grade
                    valid_components += 1
                    total_weight += 0.25
                except ValueError:
                    messagebox.showerror("Error", f"Please enter a valid grade for {component.replace('_', ' ').title()}!")
                    return
        
        if valid_components == 0:
            messagebox.showerror("Error", "Please enter at least one grade!")
            return
        
        # Calculate final grade
        if valid_components == 4:
            final_grade = sum(grades.values()) / 4
        else:
            # Get current grades for components not being updated
            conn = sqlite3.connect("class_records.db")
            cur = conn.cursor()
            cur.execute("SELECT written_works, quizzes, activities, performance_tasks FROM grades WHERE student_id = ? AND subject = ?", 
                       (student_id, self.selected_subject))
            current_grades = cur.fetchone()
            conn.close()
            
            if current_grades:
                current_grade_dict = {
                    'written_works': current_grades[0],
                    'quizzes': current_grades[1],
                    'activities': current_grades[2],
                    'performance_tasks': current_grades[3]
                }
                
                # Use updated grades where provided, otherwise use current grades
                all_grades = {}
                for component in ['written_works', 'quizzes', 'activities', 'performance_tasks']:
                    if component in grades:
                        all_grades[component] = grades[component]
                    elif current_grade_dict[component] is not None:
                        all_grades[component] = current_grade_dict[component]
                
                if all_grades:
                    final_grade = sum(all_grades.values()) / len(all_grades)
                else:
                    final_grade = 0.0
            else:
                final_grade = sum(grades.values()) / valid_components
        
        status = "Passing" if final_grade >= 75.0 else "Failing"
        
        try:
            conn = sqlite3.connect("class_records.db")
            cur = conn.cursor()
            
            # Build the update query
            update_fields = []
            update_values = []
            
            for component, grade in grades.items():
                update_fields.append(f"{component} = ?")
                update_values.append(grade)
            
            # Always update final_grade and status
            update_fields.append("final_grade = ?")
            update_values.append(round(final_grade, 1))
            
            update_fields.append("status = ?")
            update_values.append(status)
            
            update_fields.append("timestamp = ?")
            update_values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            update_values.extend([student_id, self.selected_subject])
            
            query = f"""
                UPDATE grades 
                SET {', '.join(update_fields)}
                WHERE student_id = ? AND subject = ?
            """
            
            cur.execute(query, update_values)
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Grades updated successfully!\nFinal Grade: {final_grade:.1f}% - Status: {status}")
            
            # Refresh the display
            self.load_student_data()
            self.load_grades_data_with_filters()
            self.refresh_dashboard_stats()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update grades: {str(e)}")

    def manage_subjects(self):
        self.clear_main_content()

        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header_frame,
            text="📋 Subject Management",
            font=("Arial", 28, "bold")
        ).pack(anchor="w")

        # Add New Subject Section
        add_subject_frame = ctk.CTkFrame(self.main_content)
        add_subject_frame.pack(fill="x", pady=(0, 20), padx=10)

        ctk.CTkLabel(
            add_subject_frame,
            text="Add New Subject",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(10, 10), padx=10)

        subject_form_frame = ctk.CTkFrame(add_subject_frame, fg_color="transparent")
        subject_form_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(subject_form_frame, text="Subject Name:", font=("Arial", 14)).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.new_subject_entry = ctk.CTkEntry(
            subject_form_frame,
            placeholder_text="Enter subject name",
            width=300,
            height=40
        )
        self.new_subject_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")

        ctk.CTkButton(
            subject_form_frame,
            text="➕ Add Subject",
            command=self.add_subject,
            fg_color="#2E8B57",
            hover_color="#1F5E3A",
            width=150,
            height=40
        ).grid(row=0, column=2, padx=10, pady=5)

        # Subjects List Section
        subjects_frame = ctk.CTkFrame(self.main_content)
        subjects_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            subjects_frame,
            text="Available Subjects",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(10, 10), padx=10)

        tree_container = ctk.CTkFrame(subjects_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Subject Name")
        self.subjects_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=10)

        for col in columns:
            self.subjects_tree.heading(col, text=col)
            self.subjects_tree.column(col, width=200)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.subjects_tree.yview)
        self.subjects_tree.configure(yscrollcommand=scrollbar.set)

        self.subjects_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Delete Subject Button
        delete_button_frame = ctk.CTkFrame(subjects_frame, fg_color="transparent")
        delete_button_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            delete_button_frame,
            text="🗑️ Delete Selected Subject",
            command=self.delete_subject,
            fg_color="#DC143C",
            hover_color="#B22222",
            width=200,
            height=40
        ).pack(side="left", padx=10)

        self.load_subjects()

        # Add Student to Subject Section
        add_student_frame = ctk.CTkFrame(self.main_content)
        add_student_frame.pack(fill="x", pady=20, padx=10)

        ctk.CTkLabel(
            add_student_frame,
            text="Add Student to Subject",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(10, 10), padx=10)

        student_form_frame = ctk.CTkFrame(add_student_frame, fg_color="transparent")
        student_form_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(student_form_frame, text="Select Subject:", font=("Arial", 14)).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.student_subject_combo = ctk.CTkComboBox(
            student_form_frame,
            width=200,
            height=40
        )
        self.student_subject_combo.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")

        ctk.CTkLabel(student_form_frame, text="Select Student:", font=("Arial", 14)).grid(row=0, column=2, padx=(0, 10), pady=5, sticky="w")
        self.all_students_combo = ctk.CTkComboBox(
            student_form_frame,
            width=200,
            height=40
        )
        self.all_students_combo.grid(row=0, column=3, padx=(0, 20), pady=5, sticky="w")

        ctk.CTkButton(
            student_form_frame,
            text="👨‍🎓 Add Student to Subject",
            command=self.add_student_to_subject,
            fg_color="#4169E1",
            hover_color="#2E4B8B",
            width=200,
            height=40
        ).grid(row=0, column=4, padx=10, pady=5)

        # Add New Student Section
        add_new_student_frame = ctk.CTkFrame(self.main_content)
        add_new_student_frame.pack(fill="x", pady=20, padx=10)

        ctk.CTkLabel(
            add_new_student_frame,
            text="Add New Student",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(10, 10), padx=10)

        new_student_form_frame = ctk.CTkFrame(add_new_student_frame, fg_color="transparent")
        new_student_form_frame.pack(fill="x", padx=10, pady=10)

        # Student Name
        ctk.CTkLabel(new_student_form_frame, text="Full Name:", font=("Arial", 14)).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.new_student_name_entry = ctk.CTkEntry(
            new_student_form_frame,
            placeholder_text="First Last",
            width=200,
            height=35
        )
        self.new_student_name_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")

        # Grade Level
        ctk.CTkLabel(new_student_form_frame, text="Grade Level:", font=("Arial", 14)).grid(row=0, column=2, padx=(0, 10), pady=5, sticky="w")
        self.new_student_grade_combo = ctk.CTkComboBox(
            new_student_form_frame,
            values=["9", "10", "11", "12"],
            width=150,
            height=35
        )
        self.new_student_grade_combo.set("9")
        self.new_student_grade_combo.grid(row=0, column=3, padx=(0, 20), pady=5, sticky="w")

        # Section
        ctk.CTkLabel(new_student_form_frame, text="Section:", font=("Arial", 14)).grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
        self.new_student_section_entry = ctk.CTkEntry(
            new_student_form_frame,
            placeholder_text="e.g., Grade 9 Diamond",
            width=200,
            height=35
        )
        self.new_student_section_entry.grid(row=1, column=1, padx=(0, 20), pady=5, sticky="w")

        # Add Student Button
        ctk.CTkButton(
            new_student_form_frame,
            text="👤 Add New Student",
            command=self.add_new_student,
            fg_color="#2E8B57",
            hover_color="#1F5E3A",
            width=200,
            height=40
        ).grid(row=1, column=2, padx=10, pady=5)

        self.load_subject_combo()
        self.load_all_students_combo()

    def load_subjects(self):
        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)
            
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT id, subject_name FROM subjects ORDER BY subject_name")
        subjects = cur.fetchall()
        conn.close()

        for subject in subjects:
            self.subjects_tree.insert("", "end", values=subject)

    def load_subject_combo(self):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT subject_name FROM subjects ORDER BY subject_name")
        subjects = cur.fetchall()
        conn.close()
        
        subject_list = [subject[0] for subject in subjects]
        self.student_subject_combo.configure(values=subject_list)
        if subject_list:
            self.student_subject_combo.set(subject_list[0])

    def load_all_students_combo(self):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT student_id, name, section FROM students ORDER BY name")
        students = cur.fetchall()
        conn.close()
        
        student_list = [f"{student[0]} - {student[1]} ({student[2]})" for student in students]
        self.all_students_combo.configure(values=student_list)
        if student_list:
            self.all_students_combo.set(student_list[0])

    def add_subject(self):
        subject_name = self.new_subject_entry.get().strip()
        
        if not subject_name:
            messagebox.showerror("Error", "Please enter a subject name!")
            return
            
        try:
            conn = sqlite3.connect("class_records.db")
            cur = conn.cursor()
            cur.execute("INSERT INTO subjects (subject_name) VALUES (?)", (subject_name,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Subject '{subject_name}' added successfully!")
            self.new_subject_entry.delete(0, "end")
            self.load_subjects()
            self.load_subject_combo()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Subject '{subject_name}' already exists!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add subject: {str(e)}")

    def delete_subject(self):
        selected = self.subjects_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a subject to delete!")
            return
            
        subject_id = self.subjects_tree.item(selected[0])["values"][0]
        subject_name = self.subjects_tree.item(selected[0])["values"][1]
        
        result = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete '{subject_name}'?\n\nThis will also delete all grades and attendance records for this subject!"
        )
        
        if not result:
            return
            
        try:
            conn = sqlite3.connect("class_records.db")
            cur = conn.cursor()
            
            # Delete from subjects table
            cur.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
            
            # Delete related grades
            cur.execute("DELETE FROM grades WHERE subject = ?", (subject_name,))
            
            # Delete related attendance records
            cur.execute("DELETE FROM attendance WHERE subject = ?", (subject_name,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Subject '{subject_name}' deleted successfully!")
            self.load_subjects()
            self.load_subject_combo()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete subject: {str(e)}")

    def add_new_student(self):
        name = self.new_student_name_entry.get().strip()
        grade_level = self.new_student_grade_combo.get()
        section = self.new_student_section_entry.get().strip()
        
        if not all([name, grade_level, section]):
            messagebox.showerror("Error", "Please fill in all fields!")
            return
            
        try:
            grade_level = int(grade_level)
        except ValueError:
            messagebox.showerror("Error", "Grade level must be a number!")
            return
            
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        
        try:
            # Get the highest existing student ID to auto-generate the next one
            cur.execute("SELECT student_id FROM students WHERE student_id LIKE 'S%' ORDER BY CAST(SUBSTR(student_id, 2) AS INTEGER) DESC LIMIT 1")
            result = cur.fetchone()
            
            if result:
                # Extract the number part and increment
                last_id = result[0]
                last_number = int(last_id[1:])  # Remove 'S' and convert to int
                new_number = last_number + 1
                student_id = f"S{new_number:03d}"
            else:
                # If no students exist yet, start with S001
                student_id = "S001"
            
            # Insert new student with empty subjects and attendance
            cur.execute(
                "INSERT INTO students (student_id, name, grade_level, section, subjects, attendance) VALUES (?, ?, ?, ?, ?, ?)",
                (student_id, name, grade_level, section, "{}", "{}")
            )
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Student '{name}' added successfully with ID: {student_id}!")
            
            # Clear form
            self.new_student_name_entry.delete(0, "end")
            self.new_student_section_entry.delete(0, "end")
            
            # Refresh student lists
            self.load_all_students_combo()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add student: {str(e)}")
            conn.close()

    def add_student_to_subject(self):
        subject_name = self.student_subject_combo.get()
        student_selection = self.all_students_combo.get()
        
        if not subject_name or not student_selection:
            messagebox.showerror("Error", "Please select both a subject and a student!")
            return
            
        student_id = student_selection.split(" - ")[0]
        
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM grades WHERE student_id = ? AND subject = ?", (student_id, subject_name))
        if cur.fetchone():
            messagebox.showerror("Error", "This student is already enrolled in this subject!")
            conn.close()
            return
        
        try:
            written_works = round(random.uniform(80.0, 95.0), 1)
            quizzes = round(random.uniform(75.0, 92.0), 1)
            activities = round(random.uniform(85.0, 98.0), 1)
            performance_tasks = round(random.uniform(82.0, 96.0), 1)
            final_grade = (written_works * 0.25 + quizzes * 0.25 + activities * 0.25 + performance_tasks * 0.25)
            status = "Passing" if final_grade >= 75.0 else "Failing"
            
            cur.execute("""
                INSERT INTO grades 
                (student_id, subject, written_works, quizzes, activities, performance_tasks, final_grade, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (student_id, subject_name, written_works, quizzes, activities, performance_tasks, 
                  round(final_grade, 1), status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Student added to '{subject_name}' successfully!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add student to subject: {str(e)}")
            conn.close()

    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
        self.current_stats_frame = None

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":  
    root = ctk.CTk()
    app = ClassRecordSystem(root)
    root.mainloop()
