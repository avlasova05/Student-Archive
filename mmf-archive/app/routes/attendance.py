from flask import Blueprint, jsonify, current_app

bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@bp.route('/')
def get_attendance():
    try:
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT * FROM attendance")
        attendance = cursor.fetchall()
        cursor.close()
        return jsonify(attendance)
    except Exception as e:
        return jsonify({"error": str(e)}), 500