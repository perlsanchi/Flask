from app.models import insert_user, get_user, update_user_in_db, patch_user_in_db, delete_user

# Ver 1.2 - Added Marshmallow for password validation
from marshmallow import Schema, fields, validate, ValidationError

# Ver 1.2 - JWT started
from app.models import create_jwt_token
# Ver 1.2 - JWT ended

# Ver 1.2 - Marshmallow schema for login validation
class LoginSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=1))

login_schema = LoginSchema()

def validate_user_data(data):
    """Validate user registration data"""
    if not data:
        return False, "No data provided"
    
    if "username" not in data or not data["username"]:
        return False, "Username is required"
    """Ver 1.1 commented 
    if "password" not in data or not data["password"]:
        return False, "Password is required" """
    """Ver 1.1 written - you can also write the above as"""
    if not data.get("password"):
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

""" ver 1.1 commented 
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

    return {"status": "success", "message": "Login successful"} """

""" ver 1.1 added 
def login_user(data):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"status": "error", "message": "Username and password required"}

    user = get_user(username)

    if not user:
        return {"status": "error", "message": "User not found"}

    if user["password"] != password:
        # Log failed attempt (optional)
        # log_failed_attempt(username)
        return {"status": "error", "message": "Incorrect password"}

    return {"status": "success", "message": "Login successful"} """

# Ver 1.2 - Added Marshmallow validation for login
""" ver 1.2 commented - replaced with JWT version
def login_user(data):
    # Ver 1.2 - Using Marshmallow for input validation
    try:
        validated_data = login_schema.load(data)
    except ValidationError as err:
        return {"status": "error", "message": "Validation failed", "errors": err.messages}
    
    username = validated_data.get("username")
    password = validated_data.get("password")

    user = get_user(username)

    if not user:
        return {"status": "error", "message": "User not found"}

    if user["password"] != password:
        # Ver 1.2 - Keeping the incorrect password message
        return {"status": "error", "message": "Incorrect password"}

    return {"status": "success", "message": "Login successful"} """

# Ver 1.2 - JWT started
def login_user(data):
    """Authenticate user and return JWT token"""
    # Ver 1.2 - Using Marshmallow for input validation
    try:
        validated_data = login_schema.load(data)
    except ValidationError as err:
        return {"status": "error", "message": "Validation failed", "errors": err.messages}
    
    username = validated_data.get("username")
    password = validated_data.get("password")

    user = get_user(username)

    if not user:
        return {"status": "error", "message": "User not found"}

    if user["password"] != password:
        # Ver 1.2 - Keeping the incorrect password message
        return {"status": "error", "message": "Incorrect password"}

    # Ver 1.2 - JWT: Create JWT token instead of session
    token = create_jwt_token(username)
    
    return {
        "status": "success", 
        "message": "Login successful",
        "access_token": token,
        "token_type": "Bearer",
        "username": username
    }
# Ver 1.2 - JWT ended

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