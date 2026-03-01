from app.database import db

class InstructorApplication(db.Model):
    __tablename__ = "instructor_applications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    bio = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected

    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reviewed_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=db.func.now())