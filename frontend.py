import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class LoginScreen:
    def __init__(self, root, login_callback):
        self.root = root
        self.login_callback = login_callback
        self.setup_ui()

    def setup_ui(self):
        self.clear_window()
        main_container = ctk.CTkFrame(self.root, fg_color=("gray95", "gray15"))
        main_container.pack(fill="both", expand=True)
        left_frame = ctk.CTkFrame(main_container, fg_color=("#2E8B57", "#1F5E3A"), width=400)
        left_frame.pack(side="left", fill="both", expand=False)
        left_frame.pack_propagate(False)
        brand_content = ctk.CTkFrame(left_frame, fg_color="transparent")
        brand_content.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(brand_content, text="🎓", font=("Arial", 64), text_color="white").pack(pady=10)
        ctk.CTkLabel(brand_content, text="CLASS RECORD", font=("Arial", 28, "bold"), text_color="white").pack(pady=5)
        ctk.CTkLabel(brand_content, text="Management System", font=("Arial", 16), text_color="white").pack(pady=5)
        right_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True, padx=80)
        form_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        form_frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(form_frame, text="Good Day!, Sir Meo, Sir Yno, Sir Harold", font=("Arial", 24, "bold"), text_color="#2E8B57").pack(pady=20)
        ctk.CTkLabel(form_frame, text="Teacher Login Portal", font=("Arial", 18), text_color=("gray50", "gray70")).pack(pady=5)
        ctk.CTkLabel(form_frame, text="Teacher ID", font=("Arial", 14)).pack(anchor="w", pady=(20, 5))
        self.teacher_id_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter your teacher ID", width=300, height=45, font=("Arial", 14))
        self.teacher_id_entry.pack(pady=5)
        self.teacher_id_entry.insert(0, "T001")
        ctk.CTkLabel(form_frame, text="Name", font=("Arial", 14)).pack(anchor="w", pady=(20, 5))
        self.teacher_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter your full name", width=300, height=45, font=("Arial", 14))
        self.teacher_name_entry.pack(pady=5)
        self.teacher_name_entry.insert(0, "Dr. Sarah Johnson")
        login_btn = ctk.CTkButton(form_frame, text="Sign In →", command=self.attempt_login, width=300, height=45, font=("Arial", 16, "bold"), fg_color=("#2E8B57", "#1F5E3A"), hover_color=("#1F5E3A", "#2E8B57"), corner_radius=8)
        login_btn.pack(pady=30)
        self.root.bind('<Return>', lambda event: self.attempt_login())

    def attempt_login(self):
        teacher_id = self.teacher_id_entry.get()
        name = self.teacher_name_entry.get()
        self.login_callback(teacher_id, name)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

class MainScreen:
    def __init__(self, root, current_user, backend, show_subject_callback, manage_subjects_callback, change_appearance_callback):
        self.root = root
        self.current_user = current_user
        self.backend = backend
        self.show_subject_callback = show_subject_callback
        self.manage_subjects_callback = manage_subjects_callback
        self.change_appearance_callback = change_appearance_callback
        self.current_stats_frame = None
        self.setup_ui()

    def setup_ui(self):
        self.clear_window()
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.setup_sidebar()
        self.setup_main_content()
        self.show_welcome_screen()

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        ctk.CTkLabel(self.sidebar_frame, text=" CLASS RECORDS", font=("Arial", 20, "bold")).pack(pady=(30, 10))
        ctk.CTkLabel(self.sidebar_frame, text=f"Welcome, {self.current_user[1]}", font=("Arial", 12), text_color=("gray50", "gray70")).pack(pady=(0, 30))
        nav_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15)
        ctk.CTkLabel(nav_frame, text="SUBJECTS", font=("Arial", 12, "bold"), text_color=("gray50", "gray70")).pack(anchor="w", pady=(10, 5))
        subjects = self.current_user[3].split(",")
        for subject in subjects:
            subject_btn = ctk.CTkButton(nav_frame, text=f"📚 {subject}", command=lambda subj=subject: self.show_subject_callback(subj), fg_color="transparent", hover_color=("gray80", "gray30"), anchor="w", height=40)
            subject_btn.pack(fill="x", pady=2)
        ctk.CTkLabel(nav_frame, text="MANAGEMENT", font=("Arial", 12, "bold"), text_color=("gray50", "gray70")).pack(anchor="w", pady=(20, 5))
        manage_subjects_btn = ctk.CTkButton(nav_frame, text="📋 Manage Subjects", command=self.manage_subjects_callback, fg_color="transparent", hover_color=("gray80", "gray30"), anchor="w", height=40)
        manage_subjects_btn.pack(fill="x", pady=2)
        ctk.CTkLabel(self.sidebar_frame, text="APPEARANCE", font=("Arial", 12, "bold"), text_color=("gray50", "gray70")).pack(anchor="w", pady=(30, 5), padx=15)
        appearance_mode = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_callback, width=220)
        appearance_mode.pack(pady=10, padx=15)

    def setup_main_content(self):
        self.main_content = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_welcome_screen(self):
        self.clear_main_content()
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header_frame, text="👋 Welcome Back!", font=("Arial", 28, "bold")).pack(anchor="w")
        ctk.CTkLabel(header_frame, text="Select a subject from the sidebar to manage student records", font=("Arial", 16), text_color=("gray50", "gray70")).pack(anchor="w", pady=(5, 0))
        stats_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        total_students, failing_students, total_absences = self.backend.get_system_stats()
        subjects_count = len(self.current_user[3].split(","))
        stats_data = [
            ("Students", total_students, "#2E8B57"),
            ("Failing", failing_students, "#DC143C"),
            ("Absences", total_absences, "#FF8C00"),
            ("Subjects", subjects_count, "#4169E1")
        ]
        for i, (title, value, color) in enumerate(stats_data):
            card = ctk.CTkFrame(stats_frame, width=160, height=80, border_color=color, border_width=2, corner_radius=8)
            card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=title, font=("Arial", 11, "bold"), wraplength=140).pack(pady=(8, 2))
            ctk.CTkLabel(card, text=str(value), font=("Arial", 18, "bold"), text_color=color).pack(pady=(2, 8))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def create_stats_section(self, stats_frame, subject):
        for widget in stats_frame.winfo_children():
            widget.destroy()
        total, avg_grade, failing, absences = self.backend.get_subject_stats(subject)
        stats_data = [
            ("Students", total, "#2E8B57"),
            ("Avg Grade", f"{avg_grade:.1f}%" if avg_grade else "0.0%", "#4169E1"),
            ("Failing", failing, "#DC143C"),
            ("Absences", absences, "#FF8C00")
        ]
        for i, (title, value, color) in enumerate(stats_data):
            card = ctk.CTkFrame(stats_frame, width=160, height=80, border_color=color, border_width=2, corner_radius=8)
            card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=title, font=("Arial", 11, "bold"), wraplength=140).pack(pady=(8, 2))
            ctk.CTkLabel(card, text=str(value), font=("Arial", 18, "bold"), text_color=color).pack(pady=(2, 8))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
        self.current_stats_frame = None

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()