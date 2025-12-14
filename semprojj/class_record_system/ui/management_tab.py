import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
import random
from datetime import datetime


class ManagementMixin:
    def manage_subjects(self):
        """Display subject management interface with tabs for different functions"""
        self.clear_main_content()

        manage_scroll = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="transparent"
        )
        manage_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        header_frame = ctk.CTkFrame(manage_scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header_frame,
            text="Subject Management",
            font=("Arial", 28, "bold")
        ).pack(anchor="w")

        # Create tab interface for management functions
        tabview = ctk.CTkTabview(manage_scroll)
        tabview.pack(fill="both", expand=True, pady=10)

        tabview.add("Subjects")
        tabview.add("Sections")
        tabview.add("Students")
        tabview.add("🗑️ Trash Bin")

        # Setup each management tab
        self.setup_subjects_tab(tabview.tab("Subjects"))
        self.setup_sections_tab(tabview.tab("Sections"))
        self.setup_students_tab(tabview.tab("Students"))
        self.setup_trash_tab(tabview.tab("🗑️ Trash Bin"))

    def setup_trash_tab(self, parent):
        """Create trash bin interface for restoring deleted students"""
        main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            main_frame,
            text="📁 Student Trash Bin",
            font=("Arial", 24, "bold")
        ).pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(
            main_frame,
            text="Restore accidentally deleted students with all their records",
            font=("Arial", 14),
            text_color=("gray50", "gray70")
        ).pack(anchor="w", pady=(0, 20))

        # Create treeview for deleted students
        tree_container = ctk.CTkFrame(main_frame)
        tree_container.pack(fill="both", expand=True, pady=10)

        columns = ("ID", "Student ID", "Name", "Grade Level", "Section", "Deleted From", "Deleted At", "Deleted By")
        self.trash_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=10)

        column_config = {
            "ID": 50,
            "Student ID": 100,
            "Name": 150,
            "Grade Level": 80,
            "Section": 120,
            "Deleted From": 120,
            "Deleted At": 150,
            "Deleted By": 100
        }

        for col in columns:
            self.trash_tree.heading(col, text=col)
            self.trash_tree.column(col, width=column_config[col])

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.trash_tree.yview)
        self.trash_tree.configure(yscrollcommand=scrollbar.set)

        self.trash_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Action buttons for trash bin
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            button_frame,
            text="🔄 Refresh Trash Bin",
            command=self.load_trash_bin,
            width=150,
            height=40,
            fg_color="#4169E1"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔍 View Records",
            command=self.view_trash_records,
            width=150,
            height=40,
            fg_color="#2E8B57",
            hover_color="#1F5E3A"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔄 Restore Student",
            command=self.restore_student_from_trash,
            width=180,
            height=40,
            fg_color="#2E8B57",
            hover_color="#1F5E3A"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🗑️ Permanent Delete",
            command=self.permanently_delete_from_trash,
            width=180,
            height=40,
            fg_color="#DC143C",
            hover_color="#B22222"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🗑️ Empty Trash",
            command=self.empty_trash_bin,
            width=150,
            height=40,
            fg_color="#8B0000",
            hover_color="#660000"
        ).pack(side="left", padx=5)

        # Load initial trash bin data
        self.load_trash_bin()

    def load_trash_bin(self):
        """Load deleted students from trash bin into treeview"""
        for item in self.trash_tree.get_children():
            self.trash_tree.delete(item)

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT id, original_id, student_id, name, grade_level, section, 
                   deleted_from_subject, deleted_at, deleted_by 
            FROM student_trash 
            ORDER BY deleted_at DESC
        """)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            self.trash_tree.insert("", "end", values=row)

    def view_trash_records(self):
        """Open window to view deleted student's grades and attendance"""
        selected = self.trash_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to view records!")
            return

        trash_id = self.trash_tree.item(selected[0])["values"][0]
        student_name = self.trash_tree.item(selected[0])["values"][2]
        deleted_from = self.trash_tree.item(selected[0])["values"][5]

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT grades_backup, attendance_backup FROM student_trash WHERE id = ?", (trash_id,))
        result = cur.fetchone()
        conn.close()

        if not result or not result[0]:
            messagebox.showinfo("Info", "No backup records available for this student.")
            return

        # Create modal window for records
        records_window = ctk.CTkToplevel(self.root)
        records_window.title(f"Records for {student_name}")
        records_window.geometry("800x500")
        records_window.transient(self.root)
        records_window.grab_set()

        # Center window
        window_width = 800
        window_height = 500
        screen_width = records_window.winfo_screenwidth()
        screen_height = records_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        records_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Main container
        main_container = ctk.CTkFrame(records_window)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header_frame,
            text=f"Records for {student_name}",
            font=("Arial", 20, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text=f"Deleted from: {deleted_from}",
            font=("Arial", 14),
            text_color=("gray50", "gray70")
        ).pack(anchor="w", pady=(5, 0))

        # Notebook for different record types
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill="both", expand=True, pady=10)

        # Grades tab
        grades_frame = ctk.CTkFrame(notebook, fg_color="transparent")
        notebook.add(grades_frame, text="Grades")

        grades_tree_container = ctk.CTkFrame(grades_frame)
        grades_tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        grades_columns = ("Subject", "Written Works", "Quizzes", "Activities", "Performance Tasks", "Final Grade", "Status")
        grades_tree = ttk.Treeview(grades_tree_container, columns=grades_columns, show="headings", height=8)

        grades_config = {
            "Subject": 120,
            "Written Works": 100,
            "Quizzes": 80,
            "Activities": 90,
            "Performance Tasks": 120,
            "Final Grade": 90,
            "Status": 80
        }

        for col in grades_columns:
            grades_tree.heading(col, text=col)
            grades_tree.column(col, width=grades_config[col])

        grades_scrollbar = ttk.Scrollbar(grades_tree_container, orient="vertical", command=grades_tree.yview)
        grades_tree.configure(yscrollcommand=grades_scrollbar.set)

        grades_tree.pack(side="left", fill="both", expand=True)
        grades_scrollbar.pack(side="right", fill="y")

        # Parse and display grades backup
        grades_backup = result[0]
        if grades_backup and grades_backup != "No grades backup":
            grade_lines = grades_backup.split("||")
            for line in grade_lines:
                if line:
                    parts = line.split("|")
                    if len(parts) >= 7:
                        try:
                            grades_tree.insert("", "end", values=(
                                parts[0],  # subject
                                f"{float(parts[1]):.1f}%" if parts[1] and parts[1] != 'None' else "N/A",
                                f"{float(parts[2]):.1f}%" if parts[2] and parts[2] != 'None' else "N/A",
                                f"{float(parts[3]):.1f}%" if parts[3] and parts[3] != 'None' else "N/A",
                                f"{float(parts[4]):.1f}%" if parts[4] and parts[4] != 'None' else "N/A",
                                f"{float(parts[5]):.1f}%" if parts[5] and parts[5] != 'None' else "N/A",
                                parts[6] if parts[6] else "N/A"
                            ))
                        except:
                            pass  # Skip parsing errors

        # Attendance tab
        attendance_frame = ctk.CTkFrame(notebook, fg_color="transparent")
        notebook.add(attendance_frame, text="Attendance")

        attendance_tree_container = ctk.CTkFrame(attendance_frame)
        attendance_tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        attendance_columns = ("Date", "Subject", "Status")
        attendance_tree = ttk.Treeview(attendance_tree_container, columns=attendance_columns, show="headings", height=10)

        attendance_config = {
            "Date": 120,
            "Subject": 150,
            "Status": 100
        }

        for col in attendance_columns:
            attendance_tree.heading(col, text=col)
            attendance_tree.column(col, width=attendance_config[col])

        attendance_scrollbar = ttk.Scrollbar(attendance_tree_container, orient="vertical", command=attendance_tree.yview)
        attendance_tree.configure(yscrollcommand=attendance_scrollbar.set)

        attendance_tree.pack(side="left", fill="both", expand=True)
        attendance_scrollbar.pack(side="right", fill="y")

        # Parse and display attendance backup
        attendance_backup = result[1] if len(result) > 1 else ""
        if attendance_backup and attendance_backup != "No attendance backup":
            attendance_lines = attendance_backup.split("||")
            for line in attendance_lines:
                if line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        try:
                            status_display = "Present" if parts[2] == "P" else "Absent" if parts[2] == "A" else parts[2]
                            attendance_tree.insert("", "end", values=(
                                parts[0],  # date
                                parts[1],  # subject
                                status_display
                            ))
                        except:
                            pass  # Skip parsing errors

        # Close button
        close_btn = ctk.CTkButton(
            main_container,
            text="Close",
            command=records_window.destroy,
            width=100,
            height=40
        )
        close_btn.pack(pady=10)

    def restore_student_from_trash(self):
        """Restore deleted student with all records to original subject"""
        selected = self.trash_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to restore!")
            return

        trash_id = self.trash_tree.item(selected[0])["values"][0]
        original_id = self.trash_tree.item(selected[0])["values"][1]
        student_name = self.trash_tree.item(selected[0])["values"][2]
        deleted_from = self.trash_tree.item(selected[0])["values"][5]

        # Check if original ID exists
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT student_id FROM students WHERE student_id = ?", (original_id,))
        
        new_student_id = original_id
        if cur.fetchone():
            # Generate new ID if original exists
            cur.execute("""
                SELECT student_id FROM students 
                WHERE student_id LIKE 'S%' 
                ORDER BY CAST(SUBSTR(student_id, 2) AS INTEGER) DESC LIMIT 1
            """)
            result = cur.fetchone()
            
            if result:
                last_id = result[0]
                last_number = int(last_id[1:])
                new_number = last_number + 1
                new_student_id = f"S{new_number:03d}"
            else:
                new_student_id = "S001"

        # Get student data from trash
        cur.execute("SELECT * FROM student_trash WHERE id = ?", (trash_id,))
        student_data = cur.fetchone()
        
        if student_data:
            # Restore to students table
            cur.execute("""
                INSERT INTO students (student_id, name, grade_level, section, subjects, attendance)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                new_student_id,
                student_data[3],  # name
                student_data[4],  # grade_level
                student_data[5],  # section
                student_data[6],  # subjects
                student_data[7]   # attendance
            ))
            
            # Restore grades from backup
            grades_backup = student_data[8]  # grades_backup
            if grades_backup and grades_backup != "No grades backup":
                grade_lines = grades_backup.split("||")
                for line in grade_lines:
                    if line:
                        parts = line.split("|")
                        if len(parts) >= 7 and parts[0] == deleted_from:  # Only restore for deleted subject
                            try:
                                ww = float(parts[1]) if parts[1] and parts[1] != 'None' else 0.0
                                quiz = float(parts[2]) if parts[2] and parts[2] != 'None' else 0.0
                                act = float(parts[3]) if parts[3] and parts[3] != 'None' else 0.0
                                pt = float(parts[4]) if parts[4] and parts[4] != 'None' else 0.0
                                fg = float(parts[5]) if parts[5] and parts[5] != 'None' else 0.0
                                
                                cur.execute("""
                                    INSERT INTO grades 
                                    (student_id, subject, written_works, quizzes, activities,
                                     performance_tasks, final_grade, status, timestamp)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    new_student_id,
                                    parts[0],  # subject
                                    ww,
                                    quiz,
                                    act,
                                    pt,
                                    fg,
                                    parts[6] if parts[6] else "Passing",  # status
                                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                ))
                            except Exception as e:
                                print(f"Error restoring grade: {e}")
                                pass  # Skip errors
            
            # Restore attendance from backup
            attendance_backup = student_data[9]  # attendance_backup
            if attendance_backup and attendance_backup != "No attendance backup":
                attendance_lines = attendance_backup.split("||")
                for line in attendance_lines:
                    if line:
                        parts = line.split("|")
                        if len(parts) >= 3 and parts[1] == deleted_from:  # Only restore for deleted subject
                            try:
                                cur.execute("""
                                    INSERT INTO attendance (student_id, subject, date, status)
                                    VALUES (?, ?, ?, ?)
                                """, (
                                    new_student_id,
                                    parts[1],  # subject
                                    parts[0],  # date
                                    parts[2]   # status
                                ))
                            except Exception as e:
                                print(f"Error restoring attendance: {e}")
                                pass  # Skip errors
            
            # Delete from trash
            cur.execute("DELETE FROM student_trash WHERE id = ?", (trash_id,))
            
            conn.commit()
            conn.close()
            
            message = f"Student '{student_name}' restored successfully to {deleted_from}!"
            if new_student_id != original_id:
                message += f"\nNew Student ID: {new_student_id} (original ID was already taken)"
            
            messagebox.showinfo("Success", message)
            
            self.load_trash_bin()
            self.load_sections_data()
        else:
            conn.close()
            messagebox.showerror("Error", "Student data not found in trash bin!")

    def permanently_delete_from_trash(self):
        """Permanently delete student from trash bin"""
        selected = self.trash_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to delete permanently!")
            return

        student_name = self.trash_tree.item(selected[0])["values"][2]
        
        result = messagebox.askyesno(
            "Confirm Permanent Delete",
            f"Are you sure you want to permanently delete '{student_name}'?\n" +
            "This action cannot be undone!"
        )
        
        if not result:
            return
        
        trash_id = self.trash_tree.item(selected[0])["values"][0]
        
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM student_trash WHERE id = ?", (trash_id,))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", f"Student '{student_name}' permanently deleted!")
        self.load_trash_bin()

    def empty_trash_bin(self):
        """Delete all students from trash bin permanently"""
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM student_trash")
        count = cur.fetchone()[0]
        
        if count == 0:
            conn.close()
            messagebox.showinfo("Info", "Trash bin is already empty!")
            return
        
        result = messagebox.askyesno(
            "Confirm Empty Trash",
            f"Are you sure you want to permanently delete all {count} students from trash bin?\n" +
            "This action cannot be undone!"
        )
        
        if not result:
            conn.close()
            return
        
        cur.execute("DELETE FROM student_trash")
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", f"Trash bin emptied! {count} students permanently deleted.")
        self.load_trash_bin()

    def move_student_to_trash(self, student_id, student_name, subject):
        """Move student to trash bin with backup of grades and attendance"""
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        
        # Get student data
        cur.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        student = cur.fetchone()
        
        if student:
            # Get grades for specific subject
            cur.execute("""
                SELECT subject, written_works, quizzes, activities, 
                       performance_tasks, final_grade, status 
                FROM grades 
                WHERE student_id = ? AND subject = ?
            """, (student_id, subject))
            grades = cur.fetchall()
            
            # Get attendance for specific subject
            cur.execute("""
                SELECT date, subject, status 
                FROM attendance 
                WHERE student_id = ? AND subject = ?
            """, (student_id, subject))
            attendance = cur.fetchall()
            
            # Create backup strings
            grades_backup = ""
            for grade in grades:
                grades_backup += f"{grade[0]}|{grade[1]}|{grade[2]}|{grade[3]}|{grade[4]}|{grade[5]}|{grade[6]}||"
            
            attendance_backup = ""
            for att in attendance:
                attendance_backup += f"{att[0]}|{att[1]}|{att[2]}||"
            
            # Generate unique trash ID
            import time
            trash_student_id = f"DELETED_{student_id}_{int(time.time())}"
            
            # Move to trash bin with backups
            cur.execute("""
                INSERT INTO student_trash 
                (original_id, student_id, name, grade_level, section, subjects, 
                 attendance, grades_backup, attendance_backup, deleted_from_subject,
                 deleted_at, deleted_by) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                trash_student_id,
                student[1],  # name
                student[2],  # grade_level
                student[3],  # section
                student[4],  # subjects
                student[5],  # attendance
                grades_backup if grades_backup else "No grades backup",
                attendance_backup if attendance_backup else "No attendance backup",
                subject,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.current_user[1] if hasattr(self, 'current_user') else "System"
            ))
            
            # Delete only from grades and attendance for this subject
            cur.execute("DELETE FROM grades WHERE student_id = ? AND subject = ?", 
                       (student_id, subject))
            cur.execute("DELETE FROM attendance WHERE student_id = ? AND subject = ?", 
                       (student_id, subject))
            
            conn.commit()
        
        conn.close()

    def setup_subjects_tab(self, parent):
        """Create subject management interface"""
        add_subject_frame = ctk.CTkFrame(parent)
        add_subject_frame.pack(fill="x", pady=(0, 20), padx=10)

        ctk.CTkLabel(
            add_subject_frame,
            text="Add New Subject",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(10, 10), padx=10)

        subject_form_frame = ctk.CTkFrame(add_subject_frame, fg_color="transparent")
        subject_form_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(subject_form_frame, text="Subject Name:", font=("Arial", 14)).grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky="w"
        )
        self.new_subject_entry = ctk.CTkEntry(
            subject_form_frame,
            placeholder_text="Enter subject name",
            width=300,
            height=40
        )
        self.new_subject_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")

        ctk.CTkButton(
            subject_form_frame,
            text="Add Subject",
            command=self.add_subject,
            fg_color="#2E8B57",
            hover_color="#1F5E3A",
            width=150,
            height=40
        ).grid(row=0, column=2, padx=10, pady=5)

        # Subject assignment section
        assign_subject_frame = ctk.CTkFrame(parent)
        assign_subject_frame.pack(fill="x", pady=(0, 20), padx=10)

        ctk.CTkLabel(
            assign_subject_frame,
            text="Assign Subject to Teacher",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(10, 10), padx=10)

        assign_form_frame = ctk.CTkFrame(assign_subject_frame, fg_color="transparent")
        assign_form_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(assign_form_frame, text="Select Subject:", font=("Arial", 14)).grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky="w"
        )
        self.assign_subject_combo = ctk.CTkComboBox(
            assign_form_frame,
            width=300,
            height=40
        )
        self.assign_subject_combo.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")

        self.load_assign_subject_combo()

        ctk.CTkButton(
            assign_form_frame,
            text="Assign to My Subjects",
            command=self.assign_subject_to_teacher,
            fg_color="#4169E1",
            hover_color="#2E4B8B",
            width=200,
            height=40
        ).grid(row=0, column=2, padx=10, pady=5)

        # Subject removal section
        remove_subject_frame = ctk.CTkFrame(parent)
        remove_subject_frame.pack(fill="x", pady=(0, 20), padx=10)

        ctk.CTkLabel(
            remove_subject_frame,
            text="Remove Subject from My List",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(10, 10), padx=10)

        remove_form_frame = ctk.CTkFrame(remove_subject_frame, fg_color="transparent")
        remove_form_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(remove_form_frame, text="Select Subject:", font=("Arial", 14)).grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky="w"
        )
        self.remove_subject_combo = ctk.CTkComboBox(
            remove_form_frame,
            width=300,
            height=40
        )
        self.remove_subject_combo.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")

        self.load_remove_subject_combo()

        ctk.CTkButton(
            remove_form_frame,
            text="Remove from My Subjects",
            command=self.remove_subject_from_teacher,
            fg_color="#DC143C",
            hover_color="#B22222",
            width=200,
            height=40
        ).grid(row=0, column=2, padx=10, pady=5)

        # Subjects list display
        subjects_frame = ctk.CTkFrame(parent)
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

        delete_button_frame = ctk.CTkFrame(subjects_frame, fg_color="transparent")
        delete_button_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            delete_button_frame,
            text="Delete Selected Subject",
            command=self.delete_subject,
            fg_color="#DC143C",
            hover_color="#B22222",
            width=200,
            height=40
        ).pack(side="left", padx=10)

        self.load_subjects()

    def setup_sections_tab(self, parent):
        """Create section management interface"""
        add_section_frame = ctk.CTkFrame(parent)
        add_section_frame.pack(fill="x", pady=(0, 20), padx=10)

        ctk.CTkLabel(
            add_section_frame,
            text="Add New Section",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(10, 10), padx=10)

        section_form_frame = ctk.CTkFrame(add_section_frame, fg_color="transparent")
        section_form_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(section_form_frame, text="Section Name:", font=("Arial", 14)).grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky="w"
        )
        self.new_section_entry = ctk.CTkEntry(
            section_form_frame,
            placeholder_text="Enter section name",
            width=250,
            height=40
        )
        self.new_section_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")

        ctk.CTkLabel(section_form_frame, text="Grade Level:", font=("Arial", 14)).grid(
            row=0, column=2, padx=(0, 10), pady=5, sticky="w"
        )
        self.new_section_grade = ctk.CTkComboBox(
            section_form_frame,
            values=["9", "10", "11", "12"],
            width=120,
            height=40
        )
        self.new_section_grade.set("9")
        self.new_section_grade.grid(row=0, column=3, padx=(0, 20), pady=5, sticky="w")

        ctk.CTkButton(
            section_form_frame,
            text="Add Section",
            command=self.add_new_section,
            fg_color="#2E8B57",
            hover_color="#1F5E3A",
            width=150,
            height=40
        ).grid(row=0, column=4, padx=10, pady=5)

        # Sections list display
        sections_frame = ctk.CTkFrame(parent)
        sections_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            sections_frame,
            text="Existing Sections",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(10, 10), padx=10)

        tree_container = ctk.CTkFrame(sections_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Section Name", "Grade Level", "Student Count")
        self.sections_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)

        for col in columns:
            self.sections_tree.heading(col, text=col)
            self.sections_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.sections_tree.yview)
        self.sections_tree.configure(yscrollcommand=scrollbar.set)

        self.sections_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Section action buttons
        button_frame = ctk.CTkFrame(sections_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            button_frame,
            text="Refresh Sections",
            command=self.load_sections_data,
            width=150,
            height=40,
            fg_color="#4169E1"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Delete Selected Section",
            command=self.delete_section,
            width=200,
            height=40,
            fg_color="#DC143C",
            hover_color="#B22222"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="View Section Students",
            command=self.view_section_students,
            width=180,
            height=40,
            fg_color="#2E8B57"
        ).pack(side="left", padx=5)

        self.load_sections_data()

    def delete_section(self):
        """Delete section and move all students to trash bin"""
        selected = self.sections_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a section to delete!")
            return

        section_id = self.sections_tree.item(selected[0])["values"][0]
        section_name = self.sections_tree.item(selected[0])["values"][1]
        student_count = self.sections_tree.item(selected[0])["values"][3]

        if student_count > 0:
            result = messagebox.askyesno(
                "Confirm Delete",
                f"Section '{section_name}' has {student_count} student(s). "
                f"Deleting this section will move all students to trash bin. "
                f"Are you sure you want to continue?"
            )
        else:
            result = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete section '{section_name}'?"
            )

        if not result:
            return

        try:
            conn = sqlite3.connect("class_records.db")
            cur = conn.cursor()

            # Get all students in section
            cur.execute("SELECT student_id, name FROM students WHERE section = ?", (section_name,))
            students = cur.fetchall()

            # Move each student to trash bin
            for student in students:
                student_id, student_name = student
                # Get all subjects the student is enrolled in
                cur.execute("SELECT DISTINCT subject FROM grades WHERE student_id = ?", (student_id,))
                subjects = cur.fetchall()
                for subject in subjects:
                    self.move_student_to_trash(student_id, student_name, subject[0])

            # Delete section
            cur.execute("DELETE FROM sections WHERE id = ?", (section_id,))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Section '{section_name}' deleted successfully!\n" +
                f"{student_count} students moved to trash bin."
            )

            self.load_sections_data()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete section: {str(e)}")

    def setup_students_tab(self, parent):
        """Create student management interface"""
        # Add existing student to subject
        add_student_frame = ctk.CTkFrame(parent)
        add_student_frame.pack(fill="x", pady=(0, 20), padx=10)

        ctk.CTkLabel(
            add_student_frame,
            text="Add Student to Subject",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(10, 10), padx=10)

        student_form_frame = ctk.CTkFrame(add_student_frame, fg_color="transparent")
        student_form_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(student_form_frame, text="Select Subject:", font=("Arial", 14)).grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky="w"
        )
        self.student_subject_combo = ctk.CTkComboBox(
            student_form_frame,
            width=200,
            height=40
        )
        self.student_subject_combo.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")

        ctk.CTkLabel(student_form_frame, text="Select Student:", font=("Arial", 14)).grid(
            row=0, column=2, padx=(0, 10), pady=5, sticky="w"
        )
        self.all_students_combo = ctk.CTkComboBox(
            student_form_frame,
            width=200,
            height=40
        )
        self.all_students_combo.grid(row=0, column=3, padx=(0, 20), pady=5, sticky="w")

        ctk.CTkButton(
            student_form_frame,
            text="Add Student to Subject",
            command=self.add_student_to_subject,
            fg_color="#4169E1",
            hover_color="#2E4B8B",
            width=200,
            height=40
        ).grid(row=0, column=4, padx=10, pady=5)

        # Add new student creation
        add_new_student_frame = ctk.CTkFrame(parent)
        add_new_student_frame.pack(fill="x", pady=20, padx=10)

        ctk.CTkLabel(
            add_new_student_frame,
            text="Add New Student",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(10, 10), padx=10)

        new_student_form_frame = ctk.CTkFrame(add_new_student_frame, fg_color="transparent")
        new_student_form_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(new_student_form_frame, text="Full Name:", font=("Arial", 14)).grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky="w"
        )
        self.new_student_name_entry = ctk.CTkEntry(
            new_student_form_frame,
            placeholder_text="First Last",
            width=200,
            height=35
        )
        self.new_student_name_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")

        ctk.CTkLabel(new_student_form_frame, text="Grade Level:", font=("Arial", 14)).grid(
            row=0, column=2, padx=(0, 10), pady=5, sticky="w"
        )
        self.new_student_grade_combo = ctk.CTkComboBox(
            new_student_form_frame,
            values=["9", "10", "11", "12"],
            width=150,
            height=35,
            command=self.update_section_options
        )
        self.new_student_grade_combo.set("9")
        self.new_student_grade_combo.grid(row=0, column=3, padx=(0, 20), pady=5, sticky="w")

        ctk.CTkLabel(new_student_form_frame, text="Section:", font=("Arial", 14)).grid(
            row=1, column=0, padx=(0, 10), pady=5, sticky="w"
        )
        self.new_student_section_combo = ctk.CTkComboBox(
            new_student_form_frame,
            width=200,
            height=35
        )
        self.new_student_section_combo.grid(row=1, column=1, padx=(0, 20), pady=5, sticky="w")

        self.update_section_options()

        ctk.CTkButton(
            new_student_form_frame,
            text="Add New Student",
            command=self.add_new_student,
            fg_color="#2E8B57",
            hover_color="#1F5E3A",
            width=200,
            height=40
        ).grid(row=1, column=2, padx=10, pady=5)

        self.load_subject_combo()
        self.load_all_students_combo()

    def load_sections_data(self):
        """Load sections data into treeview"""
        for item in self.sections_tree.get_children():
            self.sections_tree.delete(item)

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()

        cur.execute("SELECT id, section_name, grade_level FROM sections ORDER BY grade_level, section_name")
        sections = cur.fetchall()

        for section in sections:
            section_id, section_name, grade_level = section

            cur.execute("SELECT COUNT(*) FROM students WHERE section = ?", (section_name,))
            student_count = cur.fetchone()[0]

            self.sections_tree.insert("", "end", values=(section_id, section_name, grade_level, student_count))

        conn.close()

    def add_new_section(self):
        """Create new section in database"""
        section_name = self.new_section_entry.get().strip()
        grade_level = self.new_section_grade.get()

        if not section_name:
            messagebox.showerror("Error", "Please enter a section name!")
            return

        try:
            grade_level = int(grade_level)
            if grade_level not in [9, 10, 11, 12]:
                raise ValueError("Grade level must be between 9 and 12")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid grade level (9-12)!")
            return

        formatted_section_name = f"Grade {grade_level} {section_name}"

        try:
            conn = sqlite3.connect("class_records.db")
            cur = conn.cursor()

            # Check if section exists
            cur.execute("SELECT id FROM sections WHERE section_name = ?", (formatted_section_name,))
            if cur.fetchone():
                messagebox.showerror("Error", f"Section '{formatted_section_name}' already exists!")
                conn.close()
                return

            # Add new section
            cur.execute(
                "INSERT INTO sections (section_name, grade_level) VALUES (?, ?)",
                (formatted_section_name, grade_level)
            )

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Section '{formatted_section_name}' added successfully!")

            self.new_section_entry.delete(0, "end")
            self.load_sections_data()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add section: {str(e)}")

    def view_section_students(self):
        """Open window showing all students in selected section"""
        selected = self.sections_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a section to view!")
            return

        section_name = self.sections_tree.item(selected[0])["values"][1]

        student_window = ctk.CTkToplevel(self.root)
        student_window.title(f"Students in {section_name}")
        student_window.geometry("800x500")
        student_window.transient(self.root)
        student_window.grab_set()

        window_width = 800
        window_height = 500
        screen_width = student_window.winfo_screenwidth()
        screen_height = student_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        student_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Header
        header_frame = ctk.CTkFrame(student_window, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            header_frame,
            text=f"Students in {section_name}",
            font=("Arial", 24, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text=f"Total Students: {self.sections_tree.item(selected[0])['values'][3]}",
            font=("Arial", 14),
            text_color=("gray50", "gray70")
        ).pack(anchor="w", pady=(5, 0))

        # Students treeview
        tree_frame = ctk.CTkFrame(student_window)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("ID", "Name", "Grade Level", "Section")
        students_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        for col in columns:
            students_tree.heading(col, text=col)
            students_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=students_tree.yview)
        students_tree.configure(yscrollcommand=scrollbar.set)

        students_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load students for section
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT student_id, name, grade_level, section FROM students WHERE section = ? ORDER BY name",
            (section_name,)
        )
        students = cur.fetchall()
        conn.close()

        for student in students:
            students_tree.insert("", "end", values=student)

        # Close button
        button_frame = ctk.CTkFrame(student_window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(
            button_frame,
            text="Close",
            command=student_window.destroy,
            width=100,
            height=40
        ).pack()

    def load_subjects(self):
        """Load subjects into treeview"""
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
        """Load subjects into subject dropdown"""
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
        """Load all students into student dropdown"""
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT student_id, name, section FROM students ORDER BY name")
        students = cur.fetchall()
        conn.close()

        student_list = [f"{student[0]} - {student[1]} ({student[2]})" for student in students]
        self.all_students_combo.configure(values=student_list)
        if student_list:
            self.all_students_combo.set(student_list[0])

    def load_assign_subject_combo(self):
        """Load subjects available for assignment to teacher"""
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()

        cur.execute("SELECT subject_name FROM subjects ORDER BY subject_name")
        all_subjects = [row[0] for row in cur.fetchall()]

        teacher_subjects = self.current_user[3].split(",") if self.current_user[3] else []

        # Filter out subjects teacher already has
        available_subjects = [subj for subj in all_subjects if subj not in teacher_subjects]

        conn.close()

        self.assign_subject_combo.configure(values=available_subjects)
        if available_subjects:
            self.assign_subject_combo.set(available_subjects[0])
        else:
            self.assign_subject_combo.set("")

    def load_remove_subject_combo(self):
        """Load teacher's subjects for removal dropdown"""
        teacher_subjects = self.current_user[3].split(",") if self.current_user[3] else []

        self.remove_subject_combo.configure(values=teacher_subjects)
        if teacher_subjects and teacher_subjects[0] != "":
            self.remove_subject_combo.set(teacher_subjects[0])
        else:
            self.remove_subject_combo.set("")

    def update_section_options(self, event=None):
        """Update section dropdown based on selected grade level"""
        grade_level = self.new_student_grade_combo.get()

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT section_name FROM sections WHERE grade_level = ? ORDER BY section_name",
            (grade_level,)
        )
        sections = cur.fetchall()
        conn.close()

        section_list = [section[0] for section in sections]

        if section_list:
            self.new_student_section_combo.configure(values=section_list)
            self.new_student_section_combo.set(section_list[0])
        else:
            self.new_student_section_combo.configure(values=[])
            self.new_student_section_combo.set("")

    def add_subject(self):
        """Add new subject to database"""
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
            self.load_assign_subject_combo()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Subject '{subject_name}' already exists!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add subject: {str(e)}")

    def delete_subject(self):
        """Delete subject and all related grades/attendance"""
        selected = self.subjects_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a subject to delete!")
            return

        subject_id = self.subjects_tree.item(selected[0])["values"][0]
        subject_name = self.subjects_tree.item(selected[0])["values"][1]

        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{subject_name}'?"
        )

        if not result:
            return

        try:
            conn = sqlite3.connect("class_records.db")
            cur = conn.cursor()

            # Delete subject and all related data
            cur.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
            cur.execute("DELETE FROM grades WHERE subject = ?", (subject_name,))
            cur.execute("DELETE FROM attendance WHERE subject = ?", (subject_name,))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Subject '{subject_name}' deleted successfully!")
            self.load_subjects()
            self.load_subject_combo()
            self.load_assign_subject_combo()
            self.load_remove_subject_combo()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete subject: {str(e)}")

    def assign_subject_to_teacher(self):
        """Add subject to teacher's assigned subjects"""
        subject_name = self.assign_subject_combo.get()

        if not subject_name:
            messagebox.showerror("Error", "Please select a subject to assign!")
            return

        try:
            conn = sqlite3.connect("class_records.db")
            cur = conn.cursor()

            current_teacher = self.current_user
            current_subjects = current_teacher[3] or ""

            if subject_name not in current_subjects.split(","):
                if current_subjects:
                    updated_subjects = current_subjects + "," + subject_name
                else:
                    updated_subjects = subject_name

                # Update teacher record
                cur.execute(
                    "UPDATE teachers SET subjects = ? WHERE teacher_id = ?",
                    (updated_subjects, current_teacher[0])
                )

                # Update current user session
                self.current_user = (
                    current_teacher[0],
                    current_teacher[1],
                    current_teacher[2],
                    updated_subjects
                )

                conn.commit()
                conn.close()

                messagebox.showinfo("Success", f"Subject '{subject_name}' assigned to you successfully!")

                # Refresh UI elements
                self.refresh_sidebar_subjects()
                self.load_assign_subject_combo()
                self.load_remove_subject_combo()
            else:
                messagebox.showinfo("Info", f"You already have '{subject_name}' in your subjects!")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to assign subject: {str(e)}")

    def remove_subject_from_teacher(self):
        """Remove subject from teacher's assigned subjects"""
        subject_name = self.remove_subject_combo.get()

        if not subject_name:
            messagebox.showerror("Error", "Please select a subject to remove!")
            return

        try:
            conn = sqlite3.connect("class_records.db")
            cur = conn.cursor()

            current_teacher = self.current_user
            current_subjects = current_teacher[3] or ""

            if subject_name in current_subjects.split(","):
                subject_list = [s for s in current_subjects.split(",") if s]
                if subject_name in subject_list:
                    subject_list.remove(subject_name)
                    updated_subjects = ",".join(subject_list)

                    # Update teacher record
                    cur.execute(
                        "UPDATE teachers SET subjects = ? WHERE teacher_id = ?",
                        (updated_subjects, current_teacher[0])
                    )

                    # Update current user session
                    self.current_user = (
                        current_teacher[0],
                        current_teacher[1],
                        current_teacher[2],
                        updated_subjects
                    )

                    conn.commit()
                    conn.close()

                    messagebox.showinfo(
                        "Success",
                        f"Subject '{subject_name}' removed from your subjects!"
                    )

                    # Refresh UI elements
                    self.refresh_sidebar_subjects()
                    self.load_remove_subject_combo()
                    self.load_assign_subject_combo()
            else:
                messagebox.showinfo("Info", f"Subject '{subject_name}' is not in your subjects!")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to remove subject: {str(e)}")

    def add_new_student(self):
        """Create new student record in database"""
        name = self.new_student_name_entry.get().strip()
        grade_level = self.new_student_grade_combo.get()
        section = self.new_student_section_combo.get().strip()

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
            # Generate student ID
            cur.execute(
                "SELECT student_id FROM students WHERE student_id LIKE 'S%' "
                "ORDER BY CAST(SUBSTR(student_id, 2) AS INTEGER) DESC LIMIT 1"
            )
            result = cur.fetchone()

            if result:
                last_id = result[0]
                last_number = int(last_id[1:])
                new_number = last_number + 1
                student_id = f"S{new_number:03d}"
            else:
                student_id = "S001"

            # Verify section exists
            cur.execute("SELECT section_name FROM sections WHERE section_name = ?", (section,))
            if not cur.fetchone():
                messagebox.showerror(
                    "Error",
                    f"Section '{section}' does not exist! Please add it first in the Sections tab."
                )
                conn.close()
                return

            # Add new student
            cur.execute(
                "INSERT INTO students (student_id, name, grade_level, section, subjects, attendance) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (student_id, name, grade_level, section, "{}", "{}")
            )

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Student '{name}' added successfully with ID: {student_id}!"
            )

            # Clear form
            self.new_student_name_entry.delete(0, "end")
            self.new_student_section_combo.set("")

            # Refresh related data
            self.load_all_students_combo()
            self.load_sections_data()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add student: {str(e)}")
            conn.close()

    def add_student_to_subject(self):
        """Enroll existing student into selected subject"""
        subject_name = self.student_subject_combo.get()
        student_selection = self.all_students_combo.get()

        if not subject_name or not student_selection:
            messagebox.showerror("Error", "Please select both a subject and a student!")
            return

        student_id = student_selection.split(" - ")[0]

        # Check if student already enrolled
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM grades WHERE student_id = ? AND subject = ?",
            (student_id, subject_name)
        )
        if cur.fetchone():
            messagebox.showerror("Error", "This student is already enrolled in this subject!")
            conn.close()
            return

        try:
            # Generate sample grades for new enrollment
            written_works = round(random.uniform(80.0, 95.0), 1)
            quizzes = round(random.uniform(75.0, 92.0), 1)
            activities = round(random.uniform(85.0, 98.0), 1)
            performance_tasks = round(random.uniform(82.0, 96.0), 1)
            final_grade = (
                written_works * 0.25 +
                quizzes * 0.25 +
                activities * 0.25 +
                performance_tasks * 0.25
            )
            # Determine status based on final grade
            status = "Passing" if final_grade >= 75.0 else "Failing"

            # Add student to subject with generated grades
            cur.execute("""
                INSERT INTO grades 
                (student_id, subject, written_works, quizzes, activities, performance_tasks, 
                 final_grade, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id, subject_name, written_works, quizzes,
                activities, performance_tasks,
                round(final_grade, 1), status,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Student added to '{subject_name}' successfully!")

            self.load_all_students_combo()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add student to subject: {str(e)}")
            conn.close()