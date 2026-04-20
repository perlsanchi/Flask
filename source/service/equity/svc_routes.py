# ver 1 - cookie based login
# Ver 1.2 - JWT: Changed to JWT-based authentication

from flask import Blueprint, request, jsonify, make_response
from .services import register_user, login_user, update_user, patch_user, delete
from .models import create_session, get_session, delete_session
# Ver 1.2 - JWT started
from .models import verify_jwt_token, decode_jwt_token, blacklist_token
from functools import wraps
# Ver 1.2 - JWT ended

main = Blueprint("main", __name__)

# Ver 1.2 - JWT started: Token required decorator
def token_required(f):
    """Decorator to protect routes that require JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        if not token:
            return jsonify({
                "status": "error",
                "message": "Token is missing",
                "code": "TOKEN_MISSING"
            }), 401
        
        # Verify token
        username = verify_jwt_token(token)
        
        if not username:
            return jsonify({
                "status": "error",
                "message": "Token is invalid or expired",
                "code": "TOKEN_INVALID"
            }), 401
        
        # Pass username and token to the route function
        return f(current_user=username, token=token, *args, **kwargs)
    
    return decorated
# Ver 1.2 - JWT ended

@main.route("/")
def home():
    return "Flask Project Running"

@main.route("/users", methods=["GET"])
def get_users():
    name = request.args.get("name")  # get user with query param
    age = request.args.get("age")

    return jsonify({
        "message": "GET all users",
        "query_params": {
            "name": name,
            "age": age
        }
    })

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return "Register API is working"

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON"
        }), 400

    result = register_user(data)

    # If error
    if result["status"] == "error":
        return jsonify(result), 400

    # Success
    return jsonify(result), 201

""" ver 1.1 better error handling for incorrect password 
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return "Login api is working"

    data = request.get_json()  #forces json parsing

    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON"
        }), 400

    result = login_user(data)

    # If login failed
    if result["status"] == "error":
        return jsonify(result), 401

    # Create session and set cookie
    username = data.get("username")
    if username:
        session_id = create_session(username)

        response = make_response(jsonify({
            "status": "success",
            "message": "Login successful"
        }), 200)

        response.set_cookie(
            "session_id",
            session_id,
            httponly=True,
            secure=False,  # True in production with HTTPS
            max_age=3600,  # expiry time 1 hour
            samesite='Lax'
        )

        return response

    return jsonify(result), 200 """

""" ver 1.1 added """
""" Ver 1.2 - JWT commented out cookie version
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return "Login api is working"

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON"
        }), 400

    result = login_user(data)

    # Handle different error cases
    if result["status"] == "error":
        # Check specific error types for appropriate status codes
        if result["message"] == "User not found":
            return jsonify(result), 404
        elif result["message"] == "Incorrect password":
            return jsonify(result), 401  # Unauthorized
        else:
            return jsonify(result), 400

    # Create session and set cookie for successful login
    username = data.get("username")
    if username:
        session_id = create_session(username)

        response = make_response(jsonify({
            "status": "success",
            "message": "Login successful"
        }), 200)

        response.set_cookie(
            "session_id",
            session_id,
            httponly=True,
            secure=False,
            max_age=3600,
            samesite='Lax'
        )

        return response

    return jsonify(result), 200 """

# Ver 1.2 - JWT started
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return "Login api is working - Use POST with username/password"

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON"
        }), 400

    result = login_user(data)

    # Handle different error cases
    if result["status"] == "error":
        if result["message"] == "User not found":
            return jsonify(result), 404
        elif result["message"] == "Incorrect password":
            return jsonify(result), 401
        else:
            return jsonify(result), 400

    # Ver 1.2 - JWT: Return JWT token instead of setting cookie
    return jsonify({
        "status": "success",
        "message": "Login successful",
        "access_token": result.get("access_token"),
        "token_type": "Bearer",
        "username": result.get("username")
    }), 200
# Ver 1.2 - JWT ended

""" Ver 1.2 - JWT commented out cookie-based profile
@main.route("/profile")
def profile():
    session_id = request.cookies.get("session_id")

    if not session_id:
        return jsonify({"message": "Not logged in"}), 401

    session_data = get_session(session_id)

    if not session_data:
        return jsonify({"message": "Invalid session"}), 401

    # FIXED: Access username correctly - try different possible keys
    username = session_data.get('username') or session_data.get('username')
    
    if not username:
        print(f"Session data missing username: {session_data}")  # Debug print
        return jsonify({"message": "Session data corrupted"}), 500

    return jsonify({"message": f"Welcome {username}"}) """

# Ver 1.2 - JWT started - Protected profile route
@main.route("/profile")
@token_required
def profile(current_user, token):
    """Protected route that requires JWT token"""
    return jsonify({
        "message": f"Welcome {current_user}",
        "user": current_user,
        "status": "authenticated"
    }), 200

# Ver 1.2 - JWT started - Protected route example
@main.route("/protected")
@token_required
def protected_route(current_user, token):
    """Example of a protected route"""
    return jsonify({
        "message": f"This is protected data for user: {current_user}",
        "user": current_user,
        "data": "Sensitive information here"
    }), 200
# Ver 1.2 - JWT ended

""" Ver 1.2 - JWT commented out cookie-based logout
@main.route("/logout", methods=["POST"])
def logout():
    session_id = request.cookies.get("session_id")

    if session_id:
        delete_session(session_id)

    response = make_response(jsonify({
        "status": "success",
        "message": "Logged out"
    }))

    # Delete cookie
    response.delete_cookie("session_id")

    return response """

# Ver 1.2 - JWT Blacklist started - Proper logout with token blacklisting
@main.route("/logout", methods=["POST"])
@token_required
def logout(current_user, token):
    """Logout by blacklisting the current JWT token"""
    from datetime import datetime
    
    # Decode token to get expiry time
    payload = decode_jwt_token(token)
    
    if payload:
        expires_at = datetime.fromtimestamp(payload['exp']).isoformat()
        # Add token to blacklist
        blacklist_token(token, current_user, expires_at)
        
        return jsonify({
            "status": "success",
            "message": "Logged out successfully",
            "user": current_user,
            "timestamp": datetime.now().isoformat()
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid token"
        }), 400
# Ver 1.2 - JWT Blacklist ended

@main.route("/user/<username>", methods=["GET"])
def check_user(username):
    from .models import get_user

    user = get_user(username)

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    return jsonify({"status": "success", "message": "User exists"})

@main.route("/update-user", methods=["PUT"])
def update():
    data = request.get_json()
    result = update_user(data)

    # Create response
    response = make_response(jsonify(result), 200)

    # Add custom header -- we can see this in headers in postman
    response.headers["Custom-Header"] = "UserUpdated"

    # Set cookie (example: username)
    if data and "username" in data:
        response.set_cookie("username", data["username"])

    return response

@main.route("/user/<username>", methods=["PATCH"])
def patch(username):
    data = request.get_json()
    result = patch_user(username, data)

    if result["status"] == "error":
        return jsonify(result), 404
    
    return jsonify(result), 200

""" ver 1.1 commented 
@main.route("/user/<username>", methods=["DELETE"])
def delete_user_route(username):
    result = delete(username)

    if result["status"] == "error":
        return jsonify(result), 404
    
    return jsonify(result), 200
    """

"""ver 1.1 add custom serialization"""
from datetime import datetime
from flask import jsonify

class UserResponseSerializer:
    @staticmethod
    def serialize_delete_result(result, username, status_code):
        base_response = {
            "timestamp": datetime.now().isoformat(),
            "user": username,
            "status_code": status_code
        }
        
        if result["status"] == "error":
            base_response.update({
                "status": "error",
                "message": result["message"],
                "error_code": "DELETE_FAILED"
            })
        else:
            base_response.update({
                "status": "success",
                "message": result["message"],
                "deleted_at": datetime.now().isoformat(),
                "action": "delete_user"
            })
        
        return jsonify(base_response), status_code

@main.route("/user/<username>", methods=["DELETE"])
def delete_user_route(username):
    result = delete(username)
    
    if result["status"] == "error":
        return UserResponseSerializer.serialize_delete_result(result, username, 404)
    
    return UserResponseSerializer.serialize_delete_result(result, username, 200)

@main.route("/form-submit", methods=["POST"])
def form_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    return jsonify({
        "message": "Form submitted",
        "username": username,
        "password": "[HIDDEN]"
    })