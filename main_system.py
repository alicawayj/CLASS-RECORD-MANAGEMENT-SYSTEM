import customtkinter as ctk
from backend import DatabaseManager
from frontend import LoginScreen, MainScreen
from subject_dashboard import SubjectDashboard
from tkinter import messagebox
import sqlite3

class ClassRecordSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Class Record Management System")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        self.center_window(1400, 900)
        self.current_user = None
        self.selected_subject = None
        self.backend = DatabaseManager()
        self.login_screen()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def login_screen(self):
        self.login_ui = LoginScreen(self.root, self.check_login)

    def check_login(self, teacher_id, name):
        teacher = self.backend.check_login(teacher_id, name)
        if teacher:
            self.current_user = teacher
            self.main_screen()
        else:
            messagebox.showerror("Login Error", "Invalid teacher ID or name.")

    def main_screen(self):
        self.main_ui = MainScreen(
            self.root, 
            self.current_user, 
            self.backend,
            self.show_subject_dashboard,
            self.manage_subjects,
            self.change_appearance_mode
        )

    def show_subject_dashboard(self, subject):
        self.selected_subject = subject
        self.subject_dashboard = SubjectDashboard(
            self.main_ui.main_content,
            subject,
            self.backend,
            self.refresh_dashboard_stats
        )

    def refresh_dashboard_stats(self):
        if self.selected_subject and self.main_ui.current_stats_frame:
            self.main_ui.create_stats_section(self.main_ui.current_stats_frame, self.selected_subject)

    def manage_subjects(self):
        self.main_ui.clear_main_content()
        header_frame = ctk.CTkFrame(self.main_ui.main_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header_frame, text="📋 Subject Management", font=("Arial", 28, "bold")).pack(anchor="w")
        add_subject_frame = ctk.CTkFrame(self.main_ui.main_content)
        add_subject_frame.pack(fill="x", pady=(0, 20), padx=10)
        ctk.CTkLabel(add_subject_frame, text="Add New Subject", font=("Arial", 18, "bold")).pack(anchor="w", pady=(10, 10), padx=10)
        subject_form_frame = ctk.CTkFrame(add_subject_frame, fg_color="transparent")
        subject_form_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(subject_form_frame, text="Subject Name:", font=("Arial", 14)).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.new_subject_entry = ctk.CTkEntry(subject_form_frame, placeholder_text="Enter subject name", width=300, height=40)
        self.new_subject_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")
        ctk.CTkButton(subject_form_frame, text="➕ Add Subject", command=self.add_subject, fg_color="#2E8B57", hover_color="#1F5E3A", width=150, height=40).grid(row=0, column=2, padx=10, pady=5)
        subjects_frame = ctk.CTkFrame(self.main_ui.main_content)
        subjects_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(subjects_frame, text="Available Subjects", font=("Arial", 18, "bold")).pack(anchor="w", pady=(10, 10), padx=10)
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
        delete_button_frame = ctk.CTkFrame(subjects_frame, fg_color="transparent")
        delete_button_frame.pack(fill="x", pady=10)
        ctk.CTkButton(delete_button_frame, text="🗑️ Delete Selected Subject", command=self.delete_subject, fg_color="#DC143C", hover_color="#B22222", width=200, height=40).pack(side="left", padx=10)
        self.load_subjects()
        add_student_frame = ctk.CTkFrame(self.main_ui.main_content)
        add_student_frame.pack(fill="x", pady=20, padx=10)
        ctk.CTkLabel(add_student_frame, text="Add Student to Subject", font=("Arial", 18, "bold")).pack(anchor="w", pady=(10, 10), padx=10)
        student_form_frame = ctk.CTkFrame(add_student_frame, fg_color="transparent")
        student_form_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(student_form_frame, text="Select Subject:", font=("Arial", 14)).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.student_subject_combo = ctk.CTkComboBox(student_form_frame, width=200, height=40)
        self.student_subject_combo.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")
        ctk.CTkLabel(student_form_frame, text="Select Student:", font=("Arial", 14)).grid(row=0, column=2, padx=(0, 10), pady=5, sticky="w")
        self.all_students_combo = ctk.CTkComboBox(student_form_frame, width=200, height=40)
        self.all_students_combo.grid(row=0, column=3, padx=(0, 20), pady=5, sticky="w")
        ctk.CTkButton(student_form_frame, text="👨‍🎓 Add Student to Subject", command=self.add_student_to_subject, fg_color="#4169E1", hover_color="#2E4B8B", width=200, height=40).grid(row=0, column=4, padx=10, pady=5)
        add_new_student_frame = ctk.CTkFrame(self.main_ui.main_content)
        add_new_student_frame.pack(fill="x", pady=20, padx=10)
        ctk.CTkLabel(add_new_student_frame, text="Add New Student", font=("Arial", 18, "bold")).pack(anchor="w", pady=(10, 10), padx=10)
        new_student_form_frame = ctk.CTkFrame(add_new_student_frame, fg_color="transparent")
        new_student_form_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(new_student_form_frame, text="Full Name:", font=("Arial", 14)).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.new_student_name_entry = ctk.CTkEntry(new_student_form_frame, placeholder_text="First Last", width=200, height=35)
        self.new_student_name_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")
        ctk.CTkLabel(new_student_form_frame, text="Grade Level:", font=("Arial", 14)).grid(row=0, column=2, padx=(0, 10), pady=5, sticky="w")
        self.new_student_grade_combo = ctk.CTkComboBox(new_student_form_frame, values=["9", "10", "11", "12"], width=150, height=35)
        self.new_student_grade_combo.set("9")
        self.new_student_grade_combo.grid(row=0, column=3, padx=(0, 20), pady=5, sticky="w")
        ctk.CTkLabel(new_student_form_frame, text="Section:", font=("Arial", 14)).grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
        self.new_student_section_entry = ctk.CTkEntry(new_student_form_frame, placeholder_text="e.g., Grade 9 Diamond", width=200, height=35)
        self.new_student_section_entry.grid(row=1, column=1, padx=(0, 20), pady=5, sticky="w")
        ctk.CTkButton(new_student_form_frame, text="👤 Add New Student", command=self.add_new_student, fg_color="#2E8B57", hover_color="#1F5E3A", width=200, height=40).grid(row=1, column=2, padx=10, pady=5)
        self.load_subject_combo()
        self.load_all_students_combo()

    def load_subjects(self):
        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)
        subjects = self.backend.get_subjects()
        for subject in subjects:
            self.subjects_tree.insert("", "end", values=subject)

    def load_subject_combo(self):
        subjects = self.backend.get_subjects()
        subject_list = [subject[1] for subject in subjects]
        self.student_subject_combo.configure(values=subject_list)
        if subject_list:
            self.student_subject_combo.set(subject_list[0])

    def load_all_students_combo(self):
        students = self.backend.get_all_students()
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
            self.backend.add_subject(subject_name)
            messagebox.showinfo("Success", f"Subject '{subject_name}' added successfully!")
            self.new_subject_entry.delete(0, "end")
            self.load_subjects()
            self.load_subject_combo()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Subject '{subject_name}' already exists!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add subject: {str(e)}")

    def delete_subject(self):
        selected = self.subjects_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a subject to delete!")
            return
        subject_id = self.subjects_tree.item(selected[0])["values"][0]
        subject_name = self.subjects_tree.item(selected[0])["values"][1]
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{subject_name}'?\n\nThis will also delete all grades and attendance records for this subject!")
        if not result:
            return
        try:
            self.backend.delete_subject(subject_id, subject_name)
            messagebox.showinfo("Success", f"Subject '{subject_name}' deleted successfully!")
            self.load_subjects()
            self.load_subject_combo()
        except Exception as e:
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
        try:
            student_id = self.backend.get_next_student_id()
            self.backend.add_new_student(student_id, name, grade_level, section)
            messagebox.showinfo("Success", f"Student '{name}' added successfully with ID: {student_id}!")
            self.new_student_name_entry.delete(0, "end")
            self.new_student_section_entry.delete(0, "end")
            self.load_all_students_combo()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add student: {str(e)}")

    def add_student_to_subject(self):
        subject_name = self.student_subject_combo.get()
        student_selection = self.all_students_combo.get()
        if not subject_name or not student_selection:
            messagebox.showerror("Error", "Please select both a subject and a student!")
            return
        student_id = student_selection.split(" - ")[0]
        if self.backend.check_student_in_subject(student_id, subject_name):
            messagebox.showerror("Error", "This student is already enrolled in this subject!")
            return
        try:
            self.backend.add_student_to_subject(student_id, subject_name)
            messagebox.showinfo("Success", f"Student added to '{subject_name}' successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add student to subject: {str(e)}")

    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":  
    root = ctk.CTk()
    app = ClassRecordSystem(root)
    root.mainloop()