#!/usr/bin/env python3
"""
Test Authentication System
Simple script to test user registration and login functionality
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.auth_service import (
    register_user, 
    login_user, 
    list_users, 
    get_user_info,
    get_user_count
)


def test_authentication():
    """Test the authentication system"""
    print("🧪 Testing Authentication System")
    print("=" * 50)
    
    # Test user registration
    print("\n📝 Testing User Registration:")
    print("-" * 30)
    
    # Register test users
    test_users = [
        ("admin", "admin123", "Administrator", "admin@example.com"),
        ("john_doe", "password123", "John Doe", "john@example.com"),
        ("jane_smith", "secure456", "Jane Smith", "jane@example.com"),
    ]
    
    for username, password, full_name, email in test_users:
        success, message = register_user(username, password, full_name=full_name, email=email)
        status = "✅" if success else "❌"
        print(f"{status} {username}: {message}")
    
    # Test user listing
    print("\n👥 Testing User Listing:")
    print("-" * 30)
    
    success, message, usernames = list_users()
    if success:
        print(f"✅ {message}")
        print(f"📊 Total users: {get_user_count()}")
        for username in usernames:
            print(f"  • {username}")
    else:
        print(f"❌ {message}")
    
    # Test user login
    print("\n🔐 Testing User Login:")
    print("-" * 30)
    
    # Test valid login
    success, message = login_user("admin", "admin123")
    status = "✅" if success else "❌"
    print(f"{status} admin login: {message}")
    
    # Test invalid password
    success, message = login_user("admin", "wrongpassword")
    status = "✅" if success else "❌"
    print(f"{status} admin wrong password: {message}")
    
    # Test non-existent user
    success, message = login_user("nonexistent", "password")
    status = "✅" if success else "❌"
    print(f"{status} non-existent user: {message}")
    
    # Test user info retrieval
    print("\n👁️ Testing User Info Retrieval:")
    print("-" * 30)
    
    success, message, user_data = get_user_info("john_doe")
    if success:
        print(f"✅ {message}")
        print("📋 User details:")
        for key, value in user_data.items():
            if key != 'password_hash':  # Don't show password hash
                print(f"  {key}: {value}")
    else:
        print(f"❌ {message}")
    
    print("\n🎉 Authentication system test completed!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        test_authentication()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
