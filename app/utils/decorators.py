from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

def role_required(allowed_role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")

            if user_role not in allowed_role:
                return jsonify({"msg": "Access forbidden"}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper