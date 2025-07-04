from flask import Blueprint, jsonify, current_app, render_template, request, redirect, url_for, flash
from app.models import Student
from werkzeug.utils import secure_filename
import os

bp = Blueprint('students', __name__, url_prefix='/students')


@bp.route('/')
def get_students():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10

        search_query = request.args.get('search', '')

        sort_by = request.args.get('sort_by', 'id')
        sort_order = request.args.get('sort_order', 'asc')

        cursor = current_app.mysql.connection.cursor()

        query = "SELECT * FROM students"
        params = []

        if search_query:
            query += " WHERE full_name LIKE %s OR group_name LIKE %s"
            params.extend([f'%{search_query}%', f'%{search_query}%'])

        query += f" ORDER BY {sort_by} {sort_order}"

        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])

        cursor.execute(query, tuple(params))
        students = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM students")
        total = cursor.fetchone()[0]

        cursor.close()

        return render_template('students/list.html',
                               students=students,
                               page=page,
                               per_page=per_page,
                               total=total,
                               search_query=search_query,
                               sort_by=sort_by,
                               sort_order=sort_order)

    except Exception as e:
        current_app.logger.error(f"Error in get_students: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/<int:student_id>')
def student_details(student_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        student = Student.get_with_details(cursor, student_id)
        cursor.close()

        if not student:
            flash('Student not found', 'danger')
            return redirect(url_for('students.get_students'))

        return render_template('students/details.html', student=student)
    except Exception as e:
        current_app.logger.error(f"Error in student_details: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        try:
            full_name = request.form['full_name']
            group_name = request.form['group_name']
            photo = request.files.get('photo')

            filename = None
            if photo and photo.filename:
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

            cursor = current_app.mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO students (full_name, group_name, photo) VALUES (%s, %s, %s)",
                (full_name, group_name, filename)
            )
            current_app.mysql.connection.commit()
            cursor.close()

            flash('Student added successfully', 'success')
            return redirect(url_for('students.get_students'))

        except Exception as e:
            current_app.logger.error(f"Error adding student: {str(e)}")
            flash('Error adding student', 'danger')

    return render_template('students/add.html')


@bp.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    try:
        cursor = current_app.mysql.connection.cursor()

        if request.method == 'POST':
            full_name = request.form['full_name']
            group_name = request.form['group_name']
            photo = request.files.get('photo')

            filename = None
            if photo and photo.filename:
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                cursor.execute(
                    "UPDATE students SET full_name=%s, group_name=%s, photo=%s WHERE id=%s",
                    (full_name, group_name, filename, student_id)
                )
            else:
                cursor.execute(
                    "UPDATE students SET full_name=%s, group_name=%s WHERE id=%s",
                    (full_name, group_name, student_id)
                )

            current_app.mysql.connection.commit()
            cursor.close()
            flash('Student updated successfully', 'success')
            return redirect(url_for('students.get_students'))

        else:
            cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
            student = cursor.fetchone()
            cursor.close()

            if not student:
                flash('Student not found', 'danger')
                return redirect(url_for('students.get_students'))

            return render_template('students/edit.html', student=student)

    except Exception as e:
        current_app.logger.error(f"Error editing student: {str(e)}")
        flash('Error editing student', 'danger')
        return redirect(url_for('students.get_students'))


@bp.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        current_app.mysql.connection.commit()
        cursor.close()
        flash('Student deleted successfully', 'success')
    except Exception as e:
        current_app.logger.error(f"Error deleting student: {str(e)}")
        flash('Error deleting student', 'danger')

    return redirect(url_for('students.get_students'))
