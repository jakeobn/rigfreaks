"""
Script to update the database structure and set 'is_admin' flag for the user with ID 1.
"""
from app import app, db
from models import User

with app.app_context():
    # Create the is_admin column if it doesn't exist
    db.create_all()
    
    # Set the first user as admin
    admin_user = User.query.get(1)
    if admin_user:
        admin_user.is_admin = True
        db.session.commit()
        print(f"User '{admin_user.username}' (ID: {admin_user.id}) has been set as admin.")
    else:
        print("No user with ID 1 found to set as admin.")