"""
JSON Store Service
Manages user data storage using JSON files
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List


class JSONStore:
    """JSON-based data store for user management"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.users_file = self.data_dir / "users.json"
        self._ensure_data_dir()
        self._load_users()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        self.data_dir.mkdir(exist_ok=True)
    
    def _load_users(self):
        """Load users from JSON file"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.users = {}
        else:
            self.users = {}
            self._save_users()
    
    def _save_users(self):
        """Save users to JSON file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving users: {e}")
    
    def create_user(self, username: str, password_hash: bytes, **kwargs) -> bool:
        """Create a new user"""
        try:
            if username in self.users:
                return False
            
            user_data = {
                "username": username,
                "password_hash": password_hash.decode('utf-8'),
                "created_at": self._get_timestamp(),
                **kwargs
            }
            
            self.users[username] = user_data
            self._save_users()
            print(f"✅ Created user: {username}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return self.users.get(username)
    
    def update_user(self, username: str, **kwargs) -> bool:
        """Update user data"""
        try:
            if username not in self.users:
                return False
            
            self.users[username].update(kwargs)
            self.users[username]["updated_at"] = self._get_timestamp()
            self._save_users()
            print(f"✅ Updated user: {username}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating user: {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """Delete user"""
        try:
            if username not in self.users:
                return False
            
            del self.users[username]
            self._save_users()
            print(f"✅ Deleted user: {username}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting user: {e}")
            return False
    
    def list_users(self) -> List[str]:
        """List all usernames"""
        return list(self.users.keys())
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        return username in self.users
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        return len(self.users)
    
    def backup_users(self, backup_file: str = None) -> bool:
        """Create backup of users data"""
        try:
            if not backup_file:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"users_backup_{timestamp}.json"
            
            backup_path = self.data_dir / backup_file
            with open(backup_path, 'w') as f:
                json.dump(self.users, f, indent=2)
            
            print(f"✅ Backup created: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False
