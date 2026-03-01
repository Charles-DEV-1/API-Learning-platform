from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models.users import User
from app import mail
from app.models.Instructorapplication import InstructorApplication
from flask_mail import Message

instructor_bp = Blueprint("instructor", __name__)

@instructor_bp.route("/apply", methods=["POST"])
@jwt_required()
def apply_instructor():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.role != "student":
        return jsonify({"msg": "Only students can apply to be instructors"}), 403    

    data = request.get_json()
    bio = data.get("bio")
    experience = data.get("experience")

    if not bio or not experience:
        return jsonify({"msg": "Bio and experience are required"}), 400

    existing_application = InstructorApplication.query.filter_by(user_id=user_id, status="pending").first()
    if existing_application:
        return jsonify({"msg": "You have already applied to be an instructor"}), 400

    application = InstructorApplication(
        user_id=user_id,
        bio=bio,
        experience=experience
    )

    db.session.add(application)
    db.session.commit()

    msg = Message(
    subject="Your Password Reset OTP",
    recipients=[user.email]
    )
    msg.body = f"""
    Hello,

    You just applied to be an instructor on our platform.

    We are excited to review your application and will get back to you as soon as possible.
    You will receive an email notification once your application has been reviewed.
    Any updates regarding your application status will be communicated via email.
    Thank you for your interest in becoming an instructor!

    Best regards,
    The Team
    """
    mail.send(msg)
    return jsonify({"msg": "Instructor application submitted successfully"}), 201


@instructor_bp.route("/applications", methods=["GET"])
@jwt_required()
def view_applications():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.role != "admin":
        return jsonify({"msg": "Only admins can view instructor applications"}), 403

    applications = InstructorApplication.query.all()
    result = []
    for app in applications:
        applicant = User.query.get(app.user_id)
        result.append({
            "application_id": app.id,
            "applicant_username": applicant.username,
            "bio": app.bio,
            "experience": app.experience,
            "submitted_at": app.created_at
        })

    return jsonify(result), 200

@instructor_bp.route("/applications/<int:application_id>/", methods=["PATCH"])    
@jwt_required()
def review_application(application_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.role != "admin":
        return jsonify({"msg": "Only admins can review instructor applications"}), 403

    application = InstructorApplication.query.get(application_id)
    if not application:
        return jsonify({"msg": "Application not found"}), 404

    data = request.get_json()
    decision = data.get("decision")

    if decision not in ["approved", "rejected"]:
        return jsonify({"msg": "Decision must be 'approved' or 'rejected'"}), 400

    application.status = decision
    application.reviewed_by = user_id
    db.session.commit()

    if decision == "approved":
        applicant = User.query.get(application.user_id)
        applicant.role = "instructor"
        db.session.commit()

        msg = Message(
        subject="Instructor Application Approved",
        recipients=[applicant.email]
        )
        msg.body = f"""
        Hello,

        Congratulations! 
        Your application to become an instructor on our platform has been approved.
        You can now log in and start creating courses to share your knowledge with students around the world.
        We are excited to have you as part of our instructor community and look forward to seeing the
        amazing courses you will create!

        Thank you for your interest in becoming an instructor!

        Best regards,
        The Team
        """
        mail.send(msg)
        return jsonify({
            'message': 'Application approved and email sent to applicant'
        }), 200
    else:
        msg = Message(
        subject="Instructor Application Rejected",
        recipients=[applicant.email]
        )
        msg.body = f"""
        Hello,

        Thanks for applying for the role of an instructor on our platform,
        But unfortunately, your application has been rejected after careful review.
        We encourage you to continue learning and improving your skills, and you are welcome to reapply
        in the future if you meet the requirements.
        If you have any questions about the decision, please feel free to contact our support team.

        Thank you for your interest in becoming an instructor!

        Best regards,
        The Team
        """
        mail.send(msg)
        return jsonify({
            'message': 'Application rejected and email sent to applicant'
        }), 200    

