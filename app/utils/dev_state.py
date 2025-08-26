"""
Development State Manager
Preserves application state during hot reloads
"""

import json
import os
from pathlib import Path


class DevStateManager:
    """Manages application state during development"""
    
    def __init__(self, state_file=".dev_state.json"):
        self.state_file = Path(state_file)
        self.state = {}
        self.load_state()
    
    def load_state(self):
        """Load saved state from file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                print(f"💾 Loaded dev state: {len(self.state)} items")
            else:
                self.state = {}
                print("💾 No dev state found, starting fresh")
        except Exception as e:
            print(f"⚠️  Error loading dev state: {e}")
            self.state = {}
    
    def save_state(self):
        """Save current state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            print(f"💾 Saved dev state: {len(self.state)} items")
        except Exception as e:
            print(f"❌ Error saving dev state: {e}")
    
    def get(self, key, default=None):
        """Get a state value"""
        return self.state.get(key, default)
    
    def set(self, key, value):
        """Set a state value"""
        self.state[key] = value
    
    def delete(self, key):
        """Delete a state value"""
        if key in self.state:
            del self.state[key]
    
    def clear(self):
        """Clear all state"""
        self.state.clear()
        if self.state_file.exists():
            self.state_file.unlink()
        print("🗑️ Cleared dev state")


def save_app_state(key, value):
    """Save application state (convenience function)"""
    manager = DevStateManager()
    manager.set(key, value)
    manager.save_state()


def load_app_state(key, default=None):
    """Load application state (convenience function)"""
    manager = DevStateManager()
    return manager.get(key, default)
