from flask import Flask
from flask_mysqldb import MySQL
from config import Config
import os
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(24)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.mysql=MySQL(app)

    from app.routes import students, subjects, grades, attendance, debts, main
    app.register_blueprint(main.bp)
    app.register_blueprint(students.bp)
    app.register_blueprint(subjects.bp)
    app.register_blueprint(grades.bp)
    app.register_blueprint(attendance.bp)
    app.register_blueprint(debts.bp)

    return app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)

