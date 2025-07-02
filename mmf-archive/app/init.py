from flask import Flask
from flask_mysqldb import MySQL
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.mysql=MySQL(app)

    from app.routes import students, subjects, grades, attendance, debts
    app.register_blueprint(students.bp)
    app.register_blueprint(subjects.bp)
    app.register_blueprint(grades.bp)
    app.register_blueprint(attendance.bp)
    app.register_blueprint(debts.bp)

    return app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)