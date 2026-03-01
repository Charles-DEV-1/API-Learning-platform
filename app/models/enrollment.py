from app.database import db

class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    enrolled_at = db.Column(db.DateTime, default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint("user_id", "course_id", name="unique_enrollment"),
    )