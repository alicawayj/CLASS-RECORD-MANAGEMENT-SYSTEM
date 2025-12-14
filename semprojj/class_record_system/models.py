class Teacher:
    """Teacher model representing user accounts"""
    def __init__(self, teacher_id, name, email, subjects):
        self.teacher_id = teacher_id
        self.name = name
        self.email = email
        self.subjects = subjects


class Student:
    """Student model for academic records"""
    def __init__(self, student_id, name, grade_level, section, subjects):
        self.student_id = student_id
        self.name = name
        self.grade_level = grade_level
        self.section = section
        self.subjects = subjects
        self.attendance = {}  # Store attendance records