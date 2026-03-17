from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models.users import User
from app import mail
from app.models.course import Course
from app.models.module import Module
from flask_mail import Message

course_bp = Blueprint("course", __name__)

@course_bp.route("/courses", methods=["POST"])
@jwt_required()
def create_course():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.role != "instructor":
        return jsonify({"msg": "Only instructors can create courses"}), 403    

    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    price = data.get("price")

    if not title or not description or price is None:
        return jsonify({"msg": "Title and price and description are required"}), 400

    # Course creation logic goes here (not implemented in this snippet)
    course = Course(
            title=title,
            description=description,
            price=price,
            instructor_id=user.id
        )

    db.session.add(course)
    db.session.commit()        

    msg = Message(
    subject="Your Course Creation ",
    recipients=[user.email]
    )
    msg.body = f"""
    Hello,

    You just created a course on our platform.

    Thank you for your contribution to our learning community!
    We are excited to have your course on our platform and look forward to seeing the impact it will have on learners.
    You will receive an email notification once your course is live and available for students to enroll.

    Best regards,
    The Team
    """
    mail.send(msg)
    
    return jsonify({"msg": "Course created successfully and email notification sent"}), 201

@course_bp.route("/courses", methods=["GET"])    
def all_courses():
    courses = Course.query.filter_by(published=True).all()
    courses_data = []
    for course in courses:
        
        courses_data.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": course.price,
            "instructor_id": course.instructor_id,
            "instructor_name": course.instructor.username if course.instructor else "Unknown",
            "published": course.published
        })
    return jsonify(courses_data), 200

@course_bp.route("/courses/review/pending", methods=["GET"])
@jwt_required()
def pending_courses_for_review():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.role != "admin":
        return jsonify({"msg": "Only admins can view unpublished courses"}), 403

    courses = Course.query.filter_by(published=False).all()
    courses_data = []
    for course in courses:
        courses_data.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": course.price,
            "instructor_id": course.instructor_id,
            "instructor_name": course.instructor.username if course.instructor else "Unknown",
            "published": course.published
        })

    return jsonify(courses_data), 200


@course_bp.route("/courses/<int:course_id>/review", methods=["PATCH"])
@jwt_required()
def publish_course(course_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.role != "admin":
        return jsonify({"msg": "Only admins can review courses for publishing"}), 403

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"msg": "Course not found"}), 404

    data = request.get_json() or {}
    decision = str(data.get("decision", "")).strip().lower()
    if decision not in ["approved", "denied", "rejected"]:
        return jsonify({"msg": "Decision must be 'approved' or 'denied'"}), 400

    instructor = course.instructor
    if not instructor:
        return jsonify({"msg": "Course owner not found"}), 404

    if decision == "approved":
        course.published = True
        db.session.commit()

        msg = Message(
            subject="Your Course Has Been Published",
            recipients=[instructor.email]
        )
        msg.body = f"""
        Hello {instructor.username},

        Your course "{course.title}" has been reviewed and published on our platform.

        Thank you for your contribution to our learning community.

        Best regards,
        The Team
        """
        mail.send(msg)
        return jsonify({"msg": "Course approved and published. Email sent to instructor"}), 200

    course.published = False
    db.session.commit()

    msg = Message(
        subject="Course Review Update",
        recipients=[instructor.email]
    )
    msg.body = f"""
    Hello {instructor.username},

    Your course "{course.title}" was reviewed and was not approved for publishing at this time.

    Please review your content and submit updates if needed.

    Best regards,
    The Team
    """
    mail.send(msg)
    return jsonify({"msg": "Course review completed. Course was not published and email sent"}), 200

@course_bp.route("/courses/<int:course_id>", methods=["PATCH"])
@jwt_required()
def unpublish_course(course_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.role not in ["instructor", "admin"]:
        return jsonify({"msg": "Only instructors and admins can unpublish courses"}), 403    

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"msg": "Course not found"}), 404

    if user.role != "admin" and course.instructor_id != user.id:
        return jsonify({"msg": "You can only unpublish your own courses"}), 403

    course.published = False
    db.session.commit()

    msg = Message(
    subject="Your Course Unpublished ",
    recipients=[user.email]
    )
    msg.body = f"""
    Hello,

    Your course "{course.title}" has been unpublished on our platform.

    If you have any questions or need assistance, please feel free to contact our support team.

    Best regards,
    The Team
    """
    mail.send(msg)    
    
    return jsonify({"msg": "Course unpublished successfully and email notification sent"}), 200

@course_bp.route("/courses/me", methods=["GET"])    
@jwt_required()
def my_courses():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404  

    if user.role != "instructor":
        return jsonify({"msg": "Only instructors can view their courses"}), 403      
    courses = Course.query.filter_by(instructor_id=user_id).all()
    if not courses:
        return jsonify({"msg": "No courses found for this instructor"}), 404
    courses_data = []
    for course in courses:
        if course.instructor_id != user.id:
            return jsonify({"msg": "You can only view your own courses"}), 403
        courses_data.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": course.price,
            "instructor_id": course.instructor_id,
            "published": course.published
        })
    return jsonify(courses_data), 200

@course_bp.route("/courses/<int:course_id>/update", methods=["PATCH"])
@jwt_required()
def update_course(course_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.role != "instructor":
        return jsonify({"msg": "Only instructors can update courses"}), 403    

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"msg": "Course not found"}), 404

    if course.instructor_id != user.id:
        return jsonify({"msg": "You can only update your own courses"}), 403

    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    price = data.get("price")

    if title:
        course.title = title
    if description:
        course.description = description
    if price is not None:
        course.price = price

    db.session.commit()

    msg = Message(
    subject="Your Course Updated ",
    recipients=[user.email]
    )
    msg.body = f"""
    Hello,

    Your course "{course.title}" has been updated on our platform.

    Thank you for your contribution to our learning community!
    
    Best regards,
    The Team
    """
    mail.send(msg)    
    
    return jsonify({"msg": "Course updated successfully and email notification sent"}), 200

@course_bp.route("/courses/<int:course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.role not in ["instructor", "admin"]:
        return jsonify({"msg": "Only instructors and admins can delete courses"}), 403    

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"msg": "Course not found"}), 404

    if user.role != "admin" and course.instructor_id != user.id:
        return jsonify({"msg": "You can only delete your own courses"}), 403

    db.session.delete(course)
    db.session.commit()

    msg = Message(
        subject="Your Course Deleted",
        recipients=[user.email]
    )
    msg.body = f"""
    Hello,

    Your course "{course.title}" has been deleted from our platform.

    If you have any questions or need assistance, please feel free to contact our support team.

    Best regards,
    The Team
    """
    mail.send(msg)    
    
@course_bp.route("/courses/<int:course_id>/modules", methods=["POST"])
@jwt_required()
def create_modules(course_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"msg": "Course not found"}), 404
    if user.role != "instructor":
        return jsonify({"msg": "Only instructors can create modules"}), 403
    if course.instructor_id != user.id:
        return jsonify({"msg": "You can only create modules for your own courses"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"msg": "No input data provided"}), 400
    title = data.get("title")
    description = data.get("description")    
    if not title:
        return jsonify({"msg": "Title is required"}), 400

    last_module = Module.query.filter_by(course_id=course_id).order_by(Module.order_index.desc()).first()
    if last_module:
        new_order = last_module.order_index + 1
    else:
        new_order = 1    
    module = Module(
        title=title,
        description=description,
        course_id=course_id,
        order_index=new_order
    )
    if course.published:
        course.published = False
    db.session.add(module)    
    db.session.commit()       
    return jsonify({"id": module.id,
                    "title": module.title,
                    "order_index": module.order_index
                    }), 200


@course_bp.route("/courses/<int:course_id>/modules", methods=["GET"])
@jwt_required(optional=True)
def get_modules(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"msg": "Course not found"}), 404
    modules = Module.query.filter_by(course_id=course_id).order_by(Module.order_index).all()
    modules_list = []

        user_id = get_jwt_identity()
        if not course.published:
            return jsonify({"msg": "Course not published"}), 403
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        if user.role != "admin" and course.instructor_id != user.id:
            return jsonify({"msg": "Course not published"}), 403

    for module in modules:
        modules_list.append({
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "order_index": module.order_index
        })
    total_modules = len(modules)
    return jsonify({
        "modules": modules_list,
        "total_modules": total_modules
    }), 200
