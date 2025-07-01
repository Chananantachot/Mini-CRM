from functools import wraps
from flask import jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt

def role_required(roles):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            user_roles = claims.get('roles', [])
            # Check if any required role is in user's roles
            if not any(role in user_roles for role in roles):
                return render_template('error.html', status_code=401, msg="You are not authorized to access this page."), 401
            return fn(*args, **kwargs)
        return decorator
    return wrapper