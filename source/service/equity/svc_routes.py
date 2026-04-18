# ver 1 - cookie based login


from flask import Blueprint, request, jsonify
from .services import register_user, login_user
from .models import create_session, get_session

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return "Flask Project Running"

@main.route("/users", methods=["GET"])
def get_users():
    name = request.args.get("name")  #get user with query param
    age = request.args.get("age")

    return jsonify({
        "message": "GET all users",
        "query_params": {
            "name": name,
            "age": age
        }
    })


from flask import request, jsonify
from app.services import register_user


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

    # ❌ If error
    if result["status"] == "error":
        return jsonify(result), 400

    # ✅ Success
    return jsonify(result), 201
#cookie based login implementation started 

from flask import request, jsonify, make_response
from app.services import login_user


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return "Login api is working"

    data = request.get_json()
    token = request.headers.get("Authorization")

    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON"
        }), 400

    result = login_user(data)

    # ❌ If login failed
    if result["status"] == "error":
        return jsonify(result), 401

    # ✅ Create response
    response = make_response(jsonify(result), 200)

    # ✅ Set cookie
    username = data.get("username")
    if username:
        session_id = create_session(username)

        response = make_response(jsonify({
        "message": "Login successful"
        }))

        response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        secure=False,  # True in production
        max_age=3600  #expiry time 1 hour
        )

    return response

@main.route("/profile")
def profile():
    session_id = request.cookies.get("session_id")

    if not session_id:
        return {"message": "Not logged in"}, 401

    session_data = get_session(session_id)

    if not session_data:
        return {"message": "Invalid session"}, 401

    return {"message": f"Welcome {session_data['username']}"}

@main.route("/logout", methods=["POST"])
def logout():
    from flask import jsonify, make_response
    session_id = request.cookies.get("session_id")

    if session_id:
        delete_session(session_id)

    response = make_response(jsonify({
        "status": "success",
        "message": "Logged out"
    }))

    # ✅ Delete cookie
    response.set_cookie("username", "", expires=0)
    response.delete_cookie("session_id")

    return response

#cookie based implementation ended
  


@main.route("/user/<username>", methods=["GET"])  #get user with path param
def check_user(username):
    from app.models import get_user

    user = get_user(username)

    if not user:
        return {"status": "error", "message": "User not found"}, 404

    return {"status": "success", "message": "User exists"}

@main.route("/update-user", methods=["PUT"])
def update():
    from flask import request, jsonify, make_response
    from app.services import update_user

    data = request.get_json()
    result = update_user(data)

    # Create response
    response = make_response(jsonify(result), 200)

    # ✅ Add custom header
    response.headers["Custom-Header"] = "UserUpdated"

    # ✅ Set cookie (example: username)
    if data and "username" in data:
        response.set_cookie("username", data["username"])

    return response

@main.route("/user/<username>", methods=["PATCH"])
def patch(username):
    from flask import request, jsonify
    from app.services import patch_user

    data = request.get_json()
    result = patch_user(username, data)

    return jsonify(result)

@main.route("/user/<username>", methods = ["DELETE"])
def delete(username):
    from flask import jsonify, request
    from app.services import delete

    data = request.get_json()
    result = delete(username)

    return jsonify(result)
@main.route("/form-submit", methods=["POST"])  #form data
def form_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    return jsonify({
        "message": "Form submitted",
        "username": username
    })