"""
Script to check for existing admin users.
"""
from app import app, db
from models import User

with app.app_context():
    users = User.query.all()
    print(f"Total users: {len(users)}")
    for user in users:
        print(f"User ID: {user.id}, Username: {user.username}, Email: {user.email}")