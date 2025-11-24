import sqlite3
from datetime import datetime
import random

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

class DatabaseManager:
    def __init__(self):
        self.db_setup()
        self.generate_sample_data()

    def db_setup(self):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS teachers (teacher_id TEXT PRIMARY KEY, name TEXT, email TEXT, subjects TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS students (student_id TEXT PRIMARY KEY, name TEXT, grade_level INTEGER, section TEXT, subjects TEXT, attendance TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, subject TEXT, written_works REAL, quizzes REAL, activities REAL, performance_tasks REAL, final_grade REAL, status TEXT, timestamp TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, subject TEXT, date TEXT, status TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, subject_name TEXT UNIQUE, teacher_id TEXT)")
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
                            final_grade = (written_works * 0.25 + quizzes * 0.25 + activities * 0.25 + performance_tasks * 0.25)
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
                        cur.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", (student_id, name, grade_level, section_name, str(student_subjects), str(attendance_data)))
                        for subject, grades in student_subjects.items():
                            status = "Passing" if grades['final_grade'] >= 75.0 else "Failing"
                            cur.execute("INSERT INTO grades (student_id, subject, written_works, quizzes, activities, performance_tasks, final_grade, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (student_id, subject, grades['written_works'], grades['quizzes'], grades['activities'], grades['performance_tasks'], grades['final_grade'], status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        for subject in selected_subjects:
                            for date_str, status in attendance_data.items():
                                cur.execute("INSERT INTO attendance (student_id, subject, date, status) VALUES (?, ?, ?, ?)", (student_id, subject, date_str, status))
        conn.commit()
        conn.close()

    def check_login(self, teacher_id, name):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM teachers WHERE teacher_id = ? AND name = ?", (teacher_id, name))
        teacher = cur.fetchone()
        conn.close()
        return teacher

    def get_system_stats(self):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(DISTINCT student_id) FROM students")
        total_students = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM grades WHERE status = 'Failing'")
        failing_students = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM attendance WHERE status = 'A'")
        total_absences = cur.fetchone()[0]
        conn.close()
        return total_students, failing_students, total_absences

    def get_subject_stats(self, subject):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), AVG(final_grade), SUM(CASE WHEN status = 'Failing' THEN 1 ELSE 0 END) FROM grades WHERE subject = ?", (subject,))
        result = cur.fetchone()
        total = result[0] if result else 0
        avg_grade = result[1] if result and result[1] else 0
        failing = result[2] if result else 0
        cur.execute("SELECT COUNT(*) FROM attendance WHERE subject = ? AND status = 'A'", (subject,))
        result = cur.fetchone()
        absences = result[0] if result else 0
        conn.close()
        return total, avg_grade, failing, absences

    def get_grades_data(self, subject, section_filter="All Sections", status_filter="All", search_term=""):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        query = "SELECT s.student_id, s.name, s.grade_level, s.section, g.written_works, g.quizzes, g.activities, g.performance_tasks, g.final_grade, g.status FROM students s JOIN grades g ON s.student_id = g.student_id WHERE g.subject = ?"
        params = [subject]
        if section_filter != "All Sections":
            query += " AND s.section = ?"
            params.append(section_filter)
        if status_filter != "All":
            if status_filter == "Passing":
                query += " AND g.status = 'Passing'"
            elif status_filter == "Failing":
                query += " AND g.status = 'Failing'"
        if search_term:
            query += " AND (s.name LIKE ? OR s.student_id LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        query += " ORDER BY s.section, s.name"
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return rows

    def get_sections(self):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT section FROM students ORDER BY section")
        sections = cur.fetchall()
        conn.close()
        return [section[0] for section in sections]

    def get_attendance_data(self, subject, date_str, section_filter="All Sections"):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        if section_filter == "All Sections":
            cur.execute("SELECT s.student_id, s.name, s.grade_level, s.section, COALESCE(a.status, 'Not Marked') as status FROM students s LEFT JOIN attendance a ON s.student_id = a.student_id AND a.subject = ? AND a.date = ? WHERE EXISTS (SELECT 1 FROM grades g WHERE g.student_id = s.student_id AND g.subject = ?) ORDER BY s.section, s.name", (subject, date_str, subject))
        else:
            cur.execute("SELECT s.student_id, s.name, s.grade_level, s.section, COALESCE(a.status, 'Not Marked') as status FROM students s LEFT JOIN attendance a ON s.student_id = a.student_id AND a.subject = ? AND a.date = ? WHERE EXISTS (SELECT 1 FROM grades g WHERE g.student_id = s.student_id AND g.subject = ?) AND s.section = ? ORDER BY s.name", (subject, date_str, subject, section_filter))
        rows = cur.fetchall()
        conn.close()
        return rows

    def update_attendance(self, student_id, subject, date_str, status):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT id FROM attendance WHERE student_id = ? AND subject = ? AND date = ?", (student_id, subject, date_str))
        existing_record = cur.fetchone()
        if existing_record:
            cur.execute("UPDATE attendance SET status = ? WHERE student_id = ? AND subject = ? AND date = ?", (status, student_id, subject, date_str))
        else:
            cur.execute("INSERT INTO attendance (student_id, subject, date, status) VALUES (?, ?, ?, ?)", (student_id, subject, date_str, status))
        conn.commit()
        conn.close()

    def get_student_grades(self, student_id, subject):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT written_works, quizzes, activities, performance_tasks, final_grade, status FROM grades WHERE student_id = ? AND subject = ?", (student_id, subject))
        result = cur.fetchone()
        conn.close()
        return result

    def update_student_grades(self, student_id, subject, grades_data, final_grade, status):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        update_fields = []
        update_values = []
        for component, grade in grades_data.items():
            update_fields.append(f"{component} = ?")
            update_values.append(grade)
        update_fields.append("final_grade = ?")
        update_values.append(round(final_grade, 1))
        update_fields.append("status = ?")
        update_values.append(status)
        update_fields.append("timestamp = ?")
        update_values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        update_values.extend([student_id, subject])
        query = f"UPDATE grades SET {', '.join(update_fields)} WHERE student_id = ? AND subject = ?"
        cur.execute(query, update_values)
        conn.commit()
        conn.close()

    def get_subjects(self):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT id, subject_name FROM subjects ORDER BY subject_name")
        subjects = cur.fetchall()
        conn.close()
        return subjects

    def add_subject(self, subject_name):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO subjects (subject_name) VALUES (?)", (subject_name,))
        conn.commit()
        conn.close()

    def delete_subject(self, subject_id, subject_name):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        cur.execute("DELETE FROM grades WHERE subject = ?", (subject_name,))
        cur.execute("DELETE FROM attendance WHERE subject = ?", (subject_name,))
        conn.commit()
        conn.close()

    def get_all_students(self):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT student_id, name, section FROM students ORDER BY name")
        students = cur.fetchall()
        conn.close()
        return students

    def add_new_student(self, student_id, name, grade_level, section):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO students (student_id, name, grade_level, section, subjects, attendance) VALUES (?, ?, ?, ?, ?, ?)", (student_id, name, grade_level, section, "{}", "{}"))
        conn.commit()
        conn.close()

    def get_next_student_id(self):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT student_id FROM students WHERE student_id LIKE 'S%' ORDER BY CAST(SUBSTR(student_id, 2) AS INTEGER) DESC LIMIT 1")
        result = cur.fetchone()
        conn.close()
        if result:
            last_id = result[0]
            last_number = int(last_id[1:])
            new_number = last_number + 1
            return f"S{new_number:03d}"
        else:
            return "S001"

    def add_student_to_subject(self, student_id, subject_name):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        written_works = round(random.uniform(80.0, 95.0), 1)
        quizzes = round(random.uniform(75.0, 92.0), 1)
        activities = round(random.uniform(85.0, 98.0), 1)
        performance_tasks = round(random.uniform(82.0, 96.0), 1)
        final_grade = (written_works * 0.25 + quizzes * 0.25 + activities * 0.25 + performance_tasks * 0.25)
        status = "Passing" if final_grade >= 75.0 else "Failing"
        cur.execute("INSERT INTO grades (student_id, subject, written_works, quizzes, activities, performance_tasks, final_grade, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (student_id, subject_name, written_works, quizzes, activities, performance_tasks, round(final_grade, 1), status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

    def check_student_in_subject(self, student_id, subject_name):
        conn = sqlite3.connect("class_records.db")
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM grades WHERE student_id = ? AND subject = ?", (student_id, subject_name))
        result = cur.fetchone()
        conn.close()
        return result is not None