from app.database import db

class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    order = db.Column(db.Integer, nullable=False, default=1)
    video_url = db.Column(db.String(500), nullable=True)
    duration = db.Column(db.Integer)  # in seconds
    is_preview = db.Column(db.Boolean, default=False)

    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.now())