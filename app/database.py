from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
            from app.models.users import User
            from app.models.course import Course
            from app.models.enrollment import Enrollment
            from app.models.lesson import Lesson
            from app.models.Instructorapplication import InstructorApplication

            db.create_all()