#!/usr/bin/env python3
"""
Face Recognition Attendance System
Main application file for production use.
Uses the new modular shell structure.
"""

from shell import run_app

def main():
    """Main entry point for production attendance app"""
    print("🚀 Starting Face Recognition Attendance System (Production Mode)")
    print("=" * 60)
    
    # Run the app in production mode
    run_app(is_dev_mode=False)

if __name__ == '__main__':
    main()
