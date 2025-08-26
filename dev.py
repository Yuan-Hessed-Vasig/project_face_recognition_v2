#!/usr/bin/env python3
"""
Face Recognition Attendance System - Development Mode
Features hot module reload for development workflow
"""

import sys
import os
import time
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil
import subprocess

class HotReloadHandler(FileSystemEventHandler):
    """Handle file system events for hot reloading"""
    
    def __init__(self, dev_runner):
        self.dev_runner = dev_runner
        self.last_reload = 0
        self.reload_cooldown = 2  # Minimum seconds between reloads
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Only watch Python files
        if not event.src_path.endswith('.py'):
            return
            
        current_time = time.time()
        if current_time - self.last_reload < self.reload_cooldown:
            return
            
        print(f"🔥 File changed: {event.src_path}")
        self.dev_runner.reload_app()
        self.last_reload = current_time

class DevRunner:
    """Development runner with hot reload capability"""
    
    def __init__(self):
        self.app_process = None
        self.observer = None
        self.watch_paths = [
            "app/ui/",
            "app/services/",
            "app/database/"
        ]
        self.running = False
        
    def start_file_watcher(self):
        """Start watching for file changes"""
        self.observer = Observer()
        
        for path in self.watch_paths:
            if Path(path).exists():
                self.observer.schedule(self.hot_reload_handler, path, recursive=True)
                print(f"👀 Watching for changes in: {path}")
        
        self.observer.start()
        print("✅ File watcher started")
    
    def stop_file_watcher(self):
        """Stop watching for file changes"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("✅ File watcher stopped")
    
    def start_app(self):
        """Start the application in development mode"""
        try:
            print("🚀 Starting app in development mode...")
            
            # Use shell.py to start the app
            self.app_process = subprocess.Popen([
                sys.executable, "shell.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            print(f"✅ App started with PID: {self.app_process.pid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start app: {e}")
            return False
    
    def stop_app(self):
        """Stop the application"""
        if self.app_process:
            try:
                # Try graceful shutdown first
                self.app_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.app_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.app_process.kill()
                    self.app_process.wait()
                
                print("✅ App stopped")
                
            except Exception as e:
                print(f"❌ Error stopping app: {e}")
            finally:
                self.app_process = None
    
    def reload_app(self):
        """Reload the application"""
        print("🔄 Reloading application...")
        
        # Stop current app
        self.stop_app()
        
        # Small delay to ensure cleanup
        time.sleep(0.5)
        
        # Start new app
        self.start_app()
        
        print("✅ Application reloaded")
    
    def run(self):
        """Run the development server"""
        try:
            print("🔥 Starting Face Recognition Attendance System (Development Mode)")
            print("=" * 60)
            print("📁 Hot reload active - watching for file changes")
            print("🔄 App will automatically reload when Python files change")
            print("⏹️  Press Ctrl+C to stop")
            print("=" * 60)
            
            # Create hot reload handler
            self.hot_reload_handler = HotReloadHandler(self)
            
            # Start file watcher
            self.start_file_watcher()
            
            # Start app
            if not self.start_app():
                return
            
            self.running = True
            
            # Keep running until interrupted
            try:
                while self.running:
                    time.sleep(1)
                    
                    # Check if app process is still running
                    if self.app_process and self.app_process.poll() is not None:
                        print("⚠️  App process terminated, restarting...")
                        self.start_app()
                        
            except KeyboardInterrupt:
                print("\n🛑 Received interrupt signal")
                
        except Exception as e:
            print(f"❌ Development runner error: {e}")
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up development environment...")
        
        self.running = False
        self.stop_app()
        self.stop_file_watcher()
        
        print("✅ Development environment cleaned up")

def main():
    """Main entry point for development mode"""
    try:
        runner = DevRunner()
        runner.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Development mode stopped by user")
    except Exception as e:
        print(f"❌ Fatal error in development mode: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
