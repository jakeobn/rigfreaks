"""
Script to set a password for the existing user using direct SQL.
"""
from app import app, db
from werkzeug.security import generate_password_hash
import psycopg2
import os

# The password you want to set for the admin user
NEW_PASSWORD = "admin123"
HASHED_PASSWORD = generate_password_hash(NEW_PASSWORD)

# Connect to the database
database_url = os.environ.get("DATABASE_URL")

if database_url:
    try:
        # Connect to the database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check if the user exists
        cursor.execute("SELECT id, username, email FROM \"user\" WHERE id = 1")
        user = cursor.fetchone()
        
        if user:
            # Update the password
            cursor.execute(
                "UPDATE \"user\" SET password_hash = %s WHERE id = 1", 
                (HASHED_PASSWORD,)
            )
            conn.commit()
            
            print(f"Password for user '{user[1]}' (ID: {user[0]}) has been updated.")
            print(f"You can now login with username: {user[1]} and password: {NEW_PASSWORD}")
        else:
            print("No user with ID 1 found.")
        
        # Close the connection
        cursor.close()
        conn.close()
    
    except Exception as e:
        print(f"Error updating password: {str(e)}")
else:
    print("DATABASE_URL environment variable is not set.")