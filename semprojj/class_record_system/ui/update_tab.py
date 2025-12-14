import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime


class UpdateTabMixin:
    def setup_update_tab(self, parent):
        main_scrollable = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        main_scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        form_frame = ctk.CTkFrame(main_scrollable, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            form_frame,
            text="Update Student Grades",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=(0, 20))

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

        current_grades_frame = ctk.CTkFrame(form_frame, corner_radius=10)
        current_grades_frame.pack(fill="x", pady=15, padx=5)

        ctk.CTkLabel(
            current_grades_frame,
            text="Current Grades:",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=(12, 8), padx=12)

        grades_grid = ctk.CTkFrame(current_grades_frame, fg_color="transparent")
        grades_grid.pack(fill="x", padx=12, pady=8)

        self.current_grades_labels = {}
        grade_components = ["Written Works", "Quizzes", "Activities", "Performance Tasks", "Final Grade", "Status"]

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

        for i in range(3):
            grades_grid.columnconfigure(i, weight=1)

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

        status_frame = ctk.CTkFrame(form_frame, corner_radius=10)
        status_frame.pack(fill="x", pady=15, padx=5)

        ctk.CTkLabel(
            status_frame,
            text="Update Student Status:",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=(12, 8), padx=12)

        status_controls_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_controls_frame.pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(status_controls_frame, text="Set Status:", font=("Arial", 14)).pack(side="left", padx=(0, 10))

        self.update_status_select = ctk.CTkComboBox(
            status_controls_frame,
            values=["Passing", "Failing", "Dropped"],
            width=150,
            height=35
        )
        self.update_status_select.set("Passing")
        self.update_status_select.pack(side="left", padx=(0, 20))

        ctk.CTkButton(
            status_controls_frame,
            text="Update Status",
            command=self.update_student_status_from_update_tab,
            fg_color="#4169E1",
            hover_color="#2E4B8B",
            width=150,
            height=35
        ).pack(side="left")

        ctk.CTkLabel(
            status_controls_frame,
            text="Note: Setting status to 'Dropped' will set all grades to 0",
            font=("Arial", 11, "italic"),
            text_color="#8B0000"
        ).pack(side="left", padx=(20, 0))

        for i in range(2):
            update_grid.columnconfigure(i, weight=1)

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=25)

        ctk.CTkButton(
            button_frame,
            text="Update All Grades",
            command=self.update_student_grades,
            fg_color="#2E8B57",
            hover_color="#1F5E3A",
            width=200,
            height=45,
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Refresh Data",
            command=self.load_student_data,
            width=150,
            height=45,
            font=("Arial", 14),
            fg_color="#4169E1"
        ).pack(side="left", padx=10)

        self.load_student_data()

    def update_student_status_from_update_tab(self):
        selected = self.student_combobox.get()
        if not selected:
            messagebox.showerror("Error", "Please select a student first!")
            return

        new_status = self.update_status_select.get()
        student_id = selected.split(" - ")[0]
        student_name = selected.split(" - ")[1].split(" (")[0]

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT status FROM grades WHERE student_id = ? AND subject = ?",
            (student_id, self.selected_subject)
        )
        result = cur.fetchone()
        current_status = result[0] if result else "Unknown"
        conn.close()

        if new_status == current_status:
            messagebox.showinfo("Info", f"Student {student_name} is already marked as {current_status}")
            return

        result = messagebox.askyesno(
            "Confirm Status Update",
            f"Change status of {student_name} from {current_status} to {new_status}?"
        )

        if not result:
            return

        try:
            conn = sqlite3.connect("class_records.db")
            cur = conn.cursor()

            if new_status == "Dropped":
                cur.execute("""
                    UPDATE grades 
                    SET status = ?,
                        written_works = 0,
                        quizzes = 0,
                        activities = 0,
                        performance_tasks = 0,
                        final_grade = 0
                    WHERE student_id = ? AND subject = ?
                """, (new_status, student_id, self.selected_subject))
            else:
                cur.execute("""
                    UPDATE grades 
                    SET status = ?
                    WHERE student_id = ? AND subject = ?
                """, (new_status, student_id, self.selected_subject))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Student {student_name} status updated to {new_status}!"
            )

            self.load_student_data()
            self.load_grades_data_with_filters()
            self.refresh_dashboard_stats()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update student status: {str(e)}")

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

        selected = getattr(self, "student_combobox", None)
        if not selected:
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

            status_color = "#2E8B57"
            if grades_data["status"] == "Failing":
                status_color = "#DC143C"
            elif grades_data["status"] == "Dropped":
                status_color = "#8B0000"

            for component, value in grades_data.items():
                if component in self.current_grades_labels:
                    if component == "status":
                        self.current_grades_labels[component].configure(text=value, text_color=status_color)
                    else:
                        self.current_grades_labels[component].configure(text=value)

            if grades_data["status"] != "N/A":
                self.update_status_select.set(grades_data["status"])

            for entry in self.grade_entries.values():
                entry.delete(0, "end")

    def update_student_grades(self):
        selected = self.student_combobox.get()
        if not selected:
            messagebox.showerror("Error", "Please select a student!")
            return

        student_id = selected.split(" - ")[0]

        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT status FROM grades WHERE student_id = ? AND subject = ?",
            (student_id, self.selected_subject)
        )
        result = cur.fetchone()
        current_status = result[0] if result else ""
        conn.close()

        if current_status == "Dropped":
            result = messagebox.askyesno(
                "Student is Dropped",
                "This student is marked as Dropped. Updating grades will also change status to "
                "'Failing' or 'Passing' based on the new grade. Continue?"
            )
            if not result:
                return

        grades = {}
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
                except ValueError:
                    messagebox.showerror(
                        "Error",
                        f"Please enter a valid grade for {component.replace('_', ' ').title()}!"
                    )
                    return

        if valid_components == 0:
            messagebox.showerror("Error", "Please enter at least one grade!")
            return

        if valid_components == 4:
            final_grade = sum(grades.values()) / 4
        else:
            conn = sqlite3.connect("class_records.db")
            cur = conn.cursor()
            cur.execute("""
                SELECT written_works, quizzes, activities, performance_tasks
                FROM grades
                WHERE student_id = ? AND subject = ?
            """, (student_id, self.selected_subject))
            current_grades = cur.fetchone()
            conn.close()

            if current_grades:
                current_grade_dict = {
                    'written_works': current_grades[0],
                    'quizzes': current_grades[1],
                    'activities': current_grades[2],
                    'performance_tasks': current_grades[3]
                }

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

            update_fields = []
            update_values = []

            for component, grade in grades.items():
                update_fields.append(f"{component} = ?")
                update_values.append(grade)

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

            messagebox.showinfo(
                "Success",
                f"Grades updated successfully!\nFinal Grade: {final_grade:.1f}% - Status: {status}"
            )

            self.load_student_data()
            self.load_grades_data_with_filters()
            self.refresh_dashboard_stats()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update grades: {str(e)}")
