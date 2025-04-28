"""
Script to create an admin user for the EverCraft admin panel.
"""
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user(username, email, password):
    """Create an admin user with ID 1"""
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print(f"User '{username}' already exists. No action taken.")
        return
    
    # Check if user with ID 1 exists
    admin_user = User.query.get(1)
    if admin_user:
        print(f"Admin user with ID 1 already exists: {admin_user.username}")
        return
    
    # Create a new user with ID 1 (admin)
    user = User(
        id=1,  # Force ID 1 for admin user
        username=username,
        email=email
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    print(f"Admin user '{username}' created successfully!")

if __name__ == "__main__":
    # Create admin user with credentials
    with app.app_context():
        create_admin_user('admin', 'admin@evercraft.com', 'admin123')