from flask import Blueprint, jsonify, current_app
from flask import render_template
bp = Blueprint('students', __name__, url_prefix='/students')

@bp.route('/')
def get_students():
    try:
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        cursor.close()
        return render_template('students/list.html', students=students)
    except Exception as e:
        return jsonify({"error": str(e)}), 500