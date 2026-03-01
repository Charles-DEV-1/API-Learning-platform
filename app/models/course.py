from app.database import db

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, default=0.0)

    instructor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    published = db.Column(db.Boolean, default=False)

    modules = db.relationship("Module", backref="course", lazy=True)
    enrollments = db.relationship("Enrollment", backref="course", lazy=True)