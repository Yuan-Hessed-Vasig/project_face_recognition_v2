"""
Authentication Service
Handles user authentication and registration with bcrypt password hashing
"""

import bcrypt
from app.services.json_store import JSONStore
from typing import Tuple


def _store():
    """Get JSON store instance"""
    return JSONStore()


def register_user(username: str, password: str, **kwargs) -> Tuple[bool, str]:
    """
    Register a new user
    
    Args:
        username: Username for the new user
        password: Plain text password
        **kwargs: Additional user data (email, full_name, etc.)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not username or not password:
        return False, "Username and password are required."
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    
    if _store().get_user(username):
        return False, "Username already exists."
    
    try:
        # Hash password with bcrypt
        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        
        # Create user with additional data
        success = _store().create_user(username, pw_hash, **kwargs)
        
        if success:
            return True, "Registered successfully."
        else:
            return False, "Failed to create user."
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False, f"Registration failed: {str(e)}"


def login_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Authenticate a user
    
    Args:
        username: Username to authenticate
        password: Plain text password
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not username or not password:
        return False, "Username and password are required."
    
    try:
        user = _store().get_user(username)
        if not user:
            return False, "User not found."
        
        # Check password hash
        stored_hash = user["password_hash"].encode('utf-8')
        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            return False, "Wrong password."
        
        # Update last login timestamp
        _store().update_user(username, last_login=_store()._get_timestamp())
        
        return True, "Login success."
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False, f"Login failed: {str(e)}"


def change_password(username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    """
    Change user password
    
    Args:
        username: Username
        old_password: Current password
        new_password: New password
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not username or not old_password or not new_password:
        return False, "All fields are required."
    
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."
    
    try:
        # Verify old password first
        login_success, login_msg = login_user(username, old_password)
        if not login_success:
            return False, "Current password is incorrect."
        
        # Hash new password
        new_pw_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        
        # Update password
        success = _store().update_user(username, password_hash=new_pw_hash.decode('utf-8'))
        
        if success:
            return True, "Password changed successfully."
        else:
            return False, "Failed to update password."
            
    except Exception as e:
        print(f"❌ Password change error: {e}")
        return False, f"Password change failed: {str(e)}"


def delete_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Delete a user account
    
    Args:
        username: Username to delete
        password: Password for verification
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not username or not password:
        return False, "Username and password are required."
    
    try:
        # Verify password first
        login_success, login_msg = login_user(username, password)
        if not login_success:
            return False, "Password is incorrect."
        
        # Delete user
        success = _store().delete_user(username)
        
        if success:
            return True, "User deleted successfully."
        else:
            return False, "Failed to delete user."
            
    except Exception as e:
        print(f"❌ User deletion error: {e}")
        return False, f"User deletion failed: {str(e)}"


def get_user_info(username: str) -> Tuple[bool, str, dict]:
    """
    Get user information (without password)
    
    Args:
        username: Username to get info for
    
    Returns:
        Tuple of (success: bool, message: str, user_data: dict)
    """
    try:
        user = _store().get_user(username)
        if not user:
            return False, "User not found.", {}
        
        # Remove sensitive data
        user_info = user.copy()
        user_info.pop('password_hash', None)
        
        return True, "User found.", user_info
        
    except Exception as e:
        print(f"❌ Get user info error: {e}")
        return False, f"Failed to get user info: {str(e)}", {}


def list_users() -> Tuple[bool, str, list]:
    """
    List all users (usernames only)
    
    Returns:
        Tuple of (success: bool, message: str, usernames: list)
    """
    try:
        usernames = _store().list_users()
        return True, f"Found {len(usernames)} users.", usernames
        
    except Exception as e:
        print(f"❌ List users error: {e}")
        return False, f"Failed to list users: {str(e)}", []


def user_exists(username: str) -> bool:
    """
    Check if user exists
    
    Args:
        username: Username to check
    
    Returns:
        True if user exists, False otherwise
    """
    return _store().user_exists(username)


def get_user_count() -> int:
    """
    Get total number of users
    
    Returns:
        Number of users
    """
    return _store().get_user_count()
