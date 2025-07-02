from flask import Blueprint, jsonify, current_app
from flask import render_template
bp = Blueprint('subjects', __name__, url_prefix='/subjects')

@bp.route('/')
def get_subjects():
    try:
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()
        cursor.close()
        return render_template('subjects/list.html', subjects=subjects)
    except Exception as e:
        return jsonify({"error": str(e)}), 500