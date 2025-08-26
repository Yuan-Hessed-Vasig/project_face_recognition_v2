import mysql.connector
from mysql.connector import Error

try:
    # Connect to XAMPP MySQL server
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # XAMPP default is no password
        port=3306     # XAMPP MySQL default port
    )
    
    if mydb.is_connected():
        print("Successfully connected to XAMPP MySQL server!")
        
        # Get MySQL version
        cursor = mydb.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"MySQL Server Version: {version[0]}")
        
        cursor.close()
        mydb.close()
        print("Connection closed.")

except Error as e:
    print(f"Error connecting to MySQL: {e}")