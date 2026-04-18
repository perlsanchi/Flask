# ver 1 - cookie based login

from flask import Blueprint, request, jsonify, make_response
from .services import register_user, login_user, update_user, patch_user, delete
from .models import create_session, get_session, delete_session

main = Blueprint("main", __name__)

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

    return jsonify(result), 200

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

    return jsonify({"message": f"Welcome {username}"})

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

    return response

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

    # Add custom header
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

@main.route("/user/<username>", methods=["DELETE"])
def delete_user_route(username):
    result = delete(username)

    if result["status"] == "error":
        return jsonify(result), 404
    
    return jsonify(result), 200

@main.route("/form-submit", methods=["POST"])
def form_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    return jsonify({
        "message": "Form submitted",
        "username": username,
        "password": "[HIDDEN]"
    })