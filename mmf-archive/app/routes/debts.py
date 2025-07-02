from flask import Blueprint, jsonify, current_app

bp = Blueprint('debts', __name__, url_prefix='/debts')

@bp.route('/')
def get_debts():
    try:
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT * FROM debts")
        debts = cursor.fetchall()
        cursor.close()
        return jsonify(debts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500