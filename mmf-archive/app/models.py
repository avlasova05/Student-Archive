from datetime import datetime

class Student:
    def __init__(self, id, full_name, group_name, photo=None):
        self.id = id
        self.full_name = full_name
        self.group_name = group_name
        self.photo = photo or 'default.jpg'

    @classmethod
    def get_all(cls, cursor):
        cursor.execute("SELECT id, full_name, group_name, photo FROM students")
        return [cls(*row) for row in cursor.fetchall()]

    @classmethod
    def get_with_details(cls, cursor, student_id):
        cursor.execute("""
            SELECT id, full_name, group_name, photo 
            FROM students 
            WHERE id = %s
        """, (student_id,))
        student_data = cursor.fetchone()

        if not student_data:
            return None

        student = cls(*student_data)

        cursor.execute("""
            SELECT d.id, s.name, d.date_created, d.status, d.due_date, d.comment
            FROM debts d
            JOIN subjects s ON d.subject_id = s.id
            WHERE d.student_id = %s
        """, (student_id,))
        student.debts = cursor.fetchall()

        cursor.execute("""
            SELECT g.id, s.name, g.grade, g.status, s.type
            FROM grades g
            JOIN subjects s ON g.subject_id = s.id
            WHERE g.student_id = %s
        """, (student_id,))
        student.grades = cursor.fetchall()

        return student


class Subject:
    @classmethod
    def get_all(cls, cursor):
        cursor.execute("SELECT id, name, type FROM subjects")
        return cursor.fetchall()