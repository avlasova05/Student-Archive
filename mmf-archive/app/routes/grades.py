from flask import Blueprint, jsonify, current_app
from flask import render_template
bp = Blueprint('grades', __name__, url_prefix='/grades')

@bp.route('/')
def get_grades():
    try:
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT * FROM students")
        grades = cursor.fetchall()
        cursor.close()
        return render_template('grades/list.html', grades=grades)
    except Exception as e:
        return jsonify({"error": str(e)}), 500