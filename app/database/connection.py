"""
Database Connection Module
Handles MySQL connection using XAMPP
"""

import mysql.connector
from mysql.connector import Error
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import json

class DatabaseConnection:
    """MySQL Database Connection Manager"""
    
    def __init__(self, config_file: str = None):
        self.connection = None
        self.config = self.load_config(config_file)
        self.logger = self.setup_logger()
    
    def load_config(self, config_file: str = None) -> Dict[str, Any]:
        """Load database configuration"""
        if not config_file:
            config_file = Path(__file__).parent / "config.json"
        
        default_config = {
            "host": "localhost",
            "port": 3306,
            "database": "face_recognition_db",
            "user": "root",
            "password": "",
            "charset": "utf8mb4",
            "autocommit": True
        }
        
        try:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
                    self.logger.info("✅ Database config loaded from file")
            else:
                self.logger.warning("⚠️  No config file found, using defaults")
        except Exception as e:
            self.logger.error(f"❌ Error loading config: {e}")
        
        return default_config
    
    def setup_logger(self) -> logging.Logger:
        """Setup database logging"""
        logger = logging.getLogger('database')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            
            if self.connection.is_connected():
                self.logger.info("✅ Database connected successfully")
                return True
            else:
                self.logger.error("❌ Failed to connect to database")
                return False
                
        except Error as e:
            self.logger.error(f"❌ Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("✅ Database disconnected")
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[mysql.connector.cursor.MySQLCursor]:
        """Execute a database query"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            
            return cursor
            
        except Error as e:
            self.logger.error(f"❌ Query execution error: {e}")
            return None
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[tuple]:
        """Fetch single row from database"""
        cursor = self.execute_query(query, params)
        if cursor:
            result = cursor.fetchone()
            cursor.close()
            return result
        return None
    
    def fetch_all(self, query: str, params: tuple = None) -> list:
        """Fetch all rows from database"""
        cursor = self.execute_query(query, params)
        if cursor:
            result = cursor.fetchall()
            cursor.close()
            return result
        return []
    
    def insert(self, query: str, params: tuple = None) -> Optional[int]:
        """Insert data and return last insert ID"""
        cursor = self.execute_query(query, params)
        if cursor:
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        return None
    
    def update(self, query: str, params: tuple = None) -> int:
        """Update data and return affected rows"""
        cursor = self.execute_query(query, params)
        if cursor:
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
        return 0
    
    def delete(self, query: str, params: tuple = None) -> int:
        """Delete data and return affected rows"""
        return self.update(query, params)
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if self.connect():
                self.disconnect()
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Connection test failed: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

# Global database instance
db = DatabaseConnection()

def get_db() -> DatabaseConnection:
    """Get database connection instance"""
    return db
