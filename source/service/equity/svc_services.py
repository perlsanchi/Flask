from app.models import insert_user, get_user
from app.schemas import validate_user_data

def register_user(data):
    from app.models import insert_user
    from app.validators import validate_user_data

    # ✅ Validate
    valid, msg = validate_user_data(data)
    if not valid:
        return {"status": "error", "message": msg}

    # ✅ Insert and check result
    success = insert_user(data)

    if not success:
        return {"status": "error", "message": "User already exists"}

    return {"status": "success", "message": "User registered successfully"}

def login_user(data):

    username = data.get("username")
    password = data.get("password")

    user = get_user(username)

    if not user:
        return {"status": "error", "message": "User not found"}

    if user["password"] != password:
        return {"status": "error", "message": "Invalid password"}

    return {"status": "success", "message": "Login successful"}

def update_user(data):
    from app.models import update_user_in_db

    if not data or "username" not in data:
        return {"status": "error", "message": "Username required"}

    result = update_user_in_db(data)

    if not result:
        return {"status": "error", "message": "User not found"}

    return {"status": "success", "message": "User updated"}

def patch_user(username, data):
    from app.models import patch_user_in_db

    if not data:
        return {"status": "error", "message": "No data provided"}

    result = patch_user_in_db(username, data)

    if not result:
        return {"status": "error", "message": "User not found"}

    return {"status": "success", "message": "User updated partially"}

def delete(username):
    from app.models import delete_user
    if not username:
        return {"status": "error", "message":" User not available for deletion"}
    
    result = delete_user(username)
    
    if not result:
        return {"status":"error", "message":"User not found"}
    return {"status":"success", "message":"deletion successful"}

import sqlite3

