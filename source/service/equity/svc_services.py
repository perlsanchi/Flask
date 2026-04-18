from app.models import insert_user, get_user, update_user_in_db, patch_user_in_db, delete_user

def validate_user_data(data):
    """Validate user registration data"""
    if not data:
        return False, "No data provided"
    
    if "username" not in data or not data["username"]:
        return False, "Username is required"
    
    if "password" not in data or not data["password"]:
        return False, "Password is required"
    
    if len(data["username"]) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(data["password"]) < 4:
        return False, "Password must be at least 4 characters"
    
    return True, "Valid"

def register_user(data):
    # Validate
    valid, msg = validate_user_data(data)
    if not valid:
        return {"status": "error", "message": msg}

    # Insert and check result
    success = insert_user(data)

    if not success:
        return {"status": "error", "message": "Username already exists"}

    return {"status": "success", "message": "User registered successfully"}

def login_user(data):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"status": "error", "message": "Username and password required"}

    user = get_user(username)

    if not user:
        return {"status": "error", "message": "User not found"}

    if user["password"] != password:
        return {"status": "error", "message": "Invalid password"}

    return {"status": "success", "message": "Login successful"}

def update_user(data):
    if not data or "username" not in data:
        return {"status": "error", "message": "Username required"}

    if "password" not in data:
        return {"status": "error", "message": "Password required for update"}

    result = update_user_in_db(data)

    if not result:
        return {"status": "error", "message": "User not found"}

    return {"status": "success", "message": "User updated"}

def patch_user(username, data):
    if not data:
        return {"status": "error", "message": "No data provided"}

    result = patch_user_in_db(username, data)

    if not result:
        return {"status": "error", "message": "User not found"}

    return {"status": "success", "message": "User updated partially"}

def delete(username):
    if not username:
        return {"status": "error", "message": "User not available for deletion"}
    
    result = delete_user(username)
    
    if not result:
        return {"status": "error", "message": "User not found"}
    return {"status": "success", "message": "Deletion successful"}