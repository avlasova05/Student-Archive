from flask import Blueprint, jsonify, current_app

bp = Blueprint('attendance', __name__, url_prefix='/attendance')
@bp.route('/')
def list_attendance():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        search_query = request.args.get('search', '')

        cursor = current_app.mysql.connection.cursor()

        query = """
            SELECT a.id, s.full_name, subj.name, a.date, a.presence
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            JOIN subjects subj ON a.subject_id = subj.id
        """
        params = []

        if search_query:
            query += " WHERE s.full_name LIKE %s OR subj.name LIKE %s"
            params.extend([f'%{search_query}%', f'%{search_query}%'])

        query += " ORDER BY a.date DESC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])

        cursor.execute(query, tuple(params))
        records = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM attendance")
        total = cursor.fetchone()[0]

        cursor.close()

        return render_template('attendance/list.html',
                             records=records,
                             page=page,
                             per_page=per_page,
                             total=total,
                             search_query=search_query)

    except Exception as e:
        current_app.logger.error(f"Error in list_attendance: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route('/add', methods=['GET', 'POST'])
def add_attendance():
    if request.method == 'POST':
        try:
            student_id = request.form['student_id']
            subject_id = request.form['subject_id']
            date = request.form['date']
            presence = 1 if 'presence' in request.form else 0

            with current_app.mysql.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO attendance (student_id, subject_id, date, presence)
                    VALUES (%s, %s, %s, %s)
                """, (student_id, subject_id, date, presence))
                current_app.mysql.connection.commit()

            flash('Attendance added successfully', 'success')
            return redirect(url_for('attendance.list_attendance'))

        except Exception as e:
            current_app.logger.error(f"Error adding attendance: {e}")
            flash('Error adding attendance', 'danger')

    with current_app.mysql.connection.cursor() as cursor:
        cursor.execute("SELECT id, full_name FROM students ORDER BY full_name")
        students = cursor.fetchall()

        cursor.execute("SELECT id, name FROM subjects ORDER BY name")
        subjects = cursor.fetchall()

    current_date = datetime.now().strftime('%Y-%m-%d')

    return render_template('attendance/add.html',
                           students=students,
                           subjects=subjects,
                           current_date=current_date)


@bp.route('/edit/<int:attendance_id>', methods=['GET', 'POST'])
def edit_attendance(attendance_id):
    with current_app.mysql.connection.cursor() as cursor:
        try:
            if request.method == 'POST':
                student_id = request.form['student_id']
                subject_id = request.form['subject_id']
                date = request.form['date']
                presence = 1 if request.form.get('presence') == 'on' else 0

                cursor.execute("""
                    UPDATE attendance
                    SET student_id = %s, subject_id = %s, date = %s, presence = %s
                    WHERE id = %s
                """, (student_id, subject_id, date, presence, attendance_id))
                current_app.mysql.connection.commit()

                flash('Attendance updated successfully', 'success')
                return redirect(url_for('attendance.list_attendance'))

            cursor.execute("SELECT * FROM attendance WHERE id = %s", (attendance_id,))
            attendance = cursor.fetchone()

            if not attendance:
                flash('Attendance record not found', 'danger')
                return redirect(url_for('attendance.list_attendance'))

            cursor.execute("SELECT id, full_name FROM students ORDER BY full_name")
            students = cursor.fetchall()

            cursor.execute("SELECT id, name FROM subjects ORDER BY name")
            subjects = cursor.fetchall()

            attendance_dict = {
                'id': attendance[0],
                'student_id': attendance[1],
                'subject_id': attendance[2],
                'date': attendance[3],
                'presence': attendance[4]
            }

            return render_template('attendance/edit.html',
                                   attendance=attendance_dict,
                                   students=students,
                                   subjects=subjects)

        except Exception as e:
            current_app.logger.error(f"Error editing attendance: {e}")
            flash('Error editing attendance', 'danger')
            return redirect(url_for('attendance.list_attendance'))


@bp.route('/delete/<int:attendance_id>', methods=['POST'])
def delete_attendance(attendance_id):
    try:
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("DELETE FROM attendance WHERE id = %s", (attendance_id,))
        current_app.mysql.connection.commit()
        cursor.close()
        flash('Deleted', 'success')
    except Exception as e:
        current_app.logger.error(f"Error deleting attendance: {e}")
        flash('Error deleting', 'danger')

    return redirect(url_for('attendance.list_attendance'))
