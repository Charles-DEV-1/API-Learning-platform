from app.database import db
class Module(db.Model):
    __tablename__ = "modules"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    order = db.Column(db.Integer, nullable=False, default=1)

    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.now())

    lessons = db.relationship("Lesson", backref="module", lazy=True)