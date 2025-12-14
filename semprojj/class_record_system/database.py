import sqlite3
from datetime import datetime
import random


def db_setup():
    """Create all database tables with proper schema"""
    conn = sqlite3.connect("class_records.db")
    cur = conn.cursor()

    # Drop and recreate tables for clean setup
    cur.execute("DROP TABLE IF EXISTS teachers")
    cur.execute("""
        CREATE TABLE teachers (
            teacher_id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            subjects TEXT,
            password_hash TEXT
        )
    """)

    cur.execute("DROP TABLE IF EXISTS students")
    cur.execute("""
        CREATE TABLE students (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            grade_level INTEGER,
            section TEXT,
            subjects TEXT,
            attendance TEXT
        )
    """)

    cur.execute("DROP TABLE IF EXISTS grades")
    cur.execute("""
        CREATE TABLE grades (
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

    cur.execute("DROP TABLE IF EXISTS attendance")
    cur.execute("""
        CREATE TABLE attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            subject TEXT,
            date TEXT,
            status TEXT
        )
    """)

    cur.execute("DROP TABLE IF EXISTS subjects")
    cur.execute("""
        CREATE TABLE subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT UNIQUE,
            teacher_id TEXT
        )
    """)

    cur.execute("DROP TABLE IF EXISTS sections")
    cur.execute("""
        CREATE TABLE sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_name TEXT UNIQUE,
            grade_level INTEGER
        )
    """)

    # Create trash bin table for deleted students
    cur.execute("DROP TABLE IF EXISTS student_trash")
    cur.execute("""
        CREATE TABLE student_trash (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_id TEXT,
            student_id TEXT,
            name TEXT,
            grade_level INTEGER,
            section TEXT,
            subjects TEXT,
            attendance TEXT,
            grades_backup TEXT,
            attendance_backup TEXT,
            deleted_from_subject TEXT,
            deleted_at TEXT,
            deleted_by TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database tables created successfully!")


def simple_hash_password(password):
    """Simple password hashing using character shifting"""
    if not password:
        return ""
    
    # Simple transformation: shift each character by its position
    hash_result = ""
    for i, char in enumerate(password):
        # Shift character by its position + 5
        shifted_char = chr((ord(char) + i + 5) % 256)
        hash_result += shifted_char
    
    return hash_result


def simple_verify_password(password, stored_hash):
    """Verify password against stored hash"""
    return simple_hash_password(password) == stored_hash


def generate_sample_data():
    """Generate sample data for testing and demonstration"""
    conn = sqlite3.connect("class_records.db")
    cur = conn.cursor()

    # Default sections
    default_sections = [
        ("Grade 9 Diamond", 9),
        ("Grade 9 Ruby", 9),
        ("Grade 9 Emerald", 9),
        ("Grade 9 Sapphire", 9),
        ("Grade 9 Pearl", 9),
        ("Grade 10 Diamond", 10),
        ("Grade 10 Ruby", 10),
        ("Grade 10 Emerald", 10),
        ("Grade 10 Sapphire", 10),
        ("Grade 10 Pearl", 10),
        ("Grade 11 STEM", 11),
        ("Grade 11 ABM", 11),
        ("Grade 11 HUMSS", 11),
        ("Grade 11 GAS", 11),
        ("Grade 11 TVL", 11),
        ("Grade 12 STEM", 12),
        ("Grade 12 ABM", 12),
        ("Grade 12 HUMSS", 12),
        ("Grade 12 GAS", 12),
        ("Grade 12 TVL", 12)
    ]

    for section_name, grade_level in default_sections:
        try:
            cur.execute(
                "INSERT INTO sections (section_name, grade_level) VALUES (?, ?)",
                (section_name, grade_level)
            )
        except sqlite3.IntegrityError:
            pass  # Skip if section already exists

    # Clear existing teachers first
    cur.execute("DELETE FROM teachers")
    
    # Teachers with hashed passwords
    teachers = [
        ("T001", "Dr. Sarah Johnson", "s.johnson@school.edu", "Math,Physics", simple_hash_password("password123")),
        ("T002", "Prof. Michael Chen", "m.chen@school.edu", "Science,Biology", simple_hash_password("password123")),
        ("T003", "Ms. Emily Davis", "e.davis@school.edu", "English,Literature", simple_hash_password("password123")),
        ("T004", "Mr. Robert Wilson", "r.wilson@school.edu", "History,Geography", simple_hash_password("password123"))
    ]
    for teacher in teachers:
        cur.execute("INSERT INTO teachers VALUES (?, ?, ?, ?, ?)", teacher)

    # Available subjects
    all_subjects = [
        "Math", "Science", "English", "History",
        "Physics", "Biology", "Literature", "Geography"
    ]
    for subject in all_subjects:
        try:
            cur.execute(
                "INSERT INTO subjects (subject_name) VALUES (?)",
                (subject,)
            )
        except sqlite3.IntegrityError:
            pass  # Skip if subject already exists

    # Generate sample students
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert",
        "Jennifer", "Michael", "Linda", "William", "Elizabeth"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones",
        "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"
    ]

    sections = ["Diamond", "Ruby", "Emerald", "Sapphire", "Pearl"]
    grade_levels = [9, 10, 11, 12]

    student_count = 0
    for grade_level in grade_levels:
        for section in sections:
            for _ in range(5):
                student_count += 1
                student_id = f"S{student_count:03d}"
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                name = f"{first_name} {last_name}"
                section_name = f"Grade {grade_level} {section}"

                # Select random subjects for student
                student_subjects = {}
                num_subjects = random.randint(3, 6)
                selected_subjects = random.sample(all_subjects, num_subjects)

                for subj in selected_subjects:
                    # Generate random grades
                    written_works = round(random.uniform(80.0, 95.0), 1)
                    quizzes = round(random.uniform(75.0, 92.0), 1)
                    activities = round(random.uniform(85.0, 98.0), 1)
                    performance_tasks = round(random.uniform(82.0, 96.0), 1)

                    # Calculate final grade
                    final_grade = (
                        written_works * 0.25 +
                        quizzes * 0.25 +
                        activities * 0.25 +
                        performance_tasks * 0.25
                    )

                    # Determine status
                    if final_grade >= 75.0:
                        status = "Passing"
                    else:
                        status = "Failing"
                    
                    # Small chance of being Dropped
                    if random.random() < 0.05:  # 5% chance
                        status = "Dropped"
                        written_works = round(random.uniform(0.0, 50.0), 1)
                        quizzes = round(random.uniform(0.0, 50.0), 1)
                        activities = round(random.uniform(0.0, 50.0), 1)
                        performance_tasks = round(random.uniform(0.0, 50.0), 1)
                        final_grade = round(random.uniform(0.0, 50.0), 1)

                    student_subjects[subj] = {
                        "written_works": written_works,
                        "quizzes": quizzes,
                        "activities": activities,
                        "performance_tasks": performance_tasks,
                        "final_grade": round(final_grade, 1),
                        "status": status
                    }

                # Generate attendance data (15 days)
                attendance_data = {}
                for day in range(1, 16):
                    date_str = f"2024-01-{day:02d}"
                    attendance_data[date_str] = "P"  # All present initially

                # Insert student record
                cur.execute(
                    "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        student_id,
                        name,
                        grade_level,
                        section_name,
                        str(student_subjects),
                        str(attendance_data),
                    )
                )

                # Insert grades for each subject
                for subj, grades in student_subjects.items():
                    cur.execute(
                        """
                        INSERT INTO grades
                        (student_id, subject, written_works, quizzes, activities,
                         performance_tasks, final_grade, status, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            student_id,
                            subj,
                            grades["written_works"],
                            grades["quizzes"],
                            grades["activities"],
                            grades["performance_tasks"],
                            grades["final_grade"],
                            grades["status"],
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        )
                    )

                # Insert attendance records
                for subj in selected_subjects:
                    for date_str, st in attendance_data.items():
                        cur.execute(
                            """
                            INSERT INTO attendance (student_id, subject, date, status)
                            VALUES (?, ?, ?, ?)
                            """,
                            (student_id, subj, date_str, st)
                        )

    conn.commit()
    conn.close()
    print("Sample data generated successfully!")