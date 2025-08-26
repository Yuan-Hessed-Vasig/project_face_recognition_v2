#!/usr/bin/env python3
"""
Face Recognition Attendance System - Base Application Shell
This serves as the foundation for both main.py and dev.py
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
script_dir = Path(__file__).parent.absolute()
app_dir = script_dir / "app"

if not app_dir.exists():
    print(f"❌ App directory not found: {app_dir}")
    sys.exit(1)

# Add app directory to Python path
sys.path.insert(0, str(app_dir))

try:
    # Import the base app from the app package
    from app.ui.app import Root
    print("✅ Successfully imported base app shell")
except ImportError as e:
    print(f"❌ Failed to import base app shell: {e}")
    print(f"📁 App directory: {app_dir}")
    print(f"📁 Available files: {list(app_dir.glob('*.py'))}")
    sys.exit(1)

def create_app(is_dev_mode=False):
    """Create app instance with specified mode"""
    try:
        print(f"🚀 Creating {'development' if is_dev_mode else 'production'} app...")
        app = Root(is_dev_mode=is_dev_mode)
        return app
    except Exception as e:
        print(f"❌ Failed to create app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def run_app(is_dev_mode=False):
    """Create and run the application"""
    try:
        app = create_app(is_dev_mode)
        app.run()
    except KeyboardInterrupt:
        print("\n🛑 Received keyboard interrupt, shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("✅ Application closed.")

if __name__ == '__main__':
    # Default to production mode when run directly
    run_app(is_dev_mode=False)
