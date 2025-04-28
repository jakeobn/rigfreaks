from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, send_from_directory
from models import db, ContactMessage, User, Build, PreBuiltConfig
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
import logging
import os
import json
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# Admin login check decorator (custom for admin panel)
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in to access the admin area.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin role required decorator
def admin_required(f):
    @wraps(f)
    @admin_login_required  # First ensure the admin is logged in
    def decorated_function(*args, **kwargs):
        # For simplicity, we'll just check if the user ID is 1
        # In a real-world app, you'd check for an is_admin flag
        admin_id = session.get('admin_id')
        if admin_id == 1:
            return f(*args, **kwargs)
        else:
            flash('You do not have administrator privileges.', 'danger')
            return redirect(url_for('index'))
    return decorated_function

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # For this demo, we'll hardcode admin credentials
        # In a real app, you would check credentials from the database
        if username == "Jake" and password == "admin123":
            session['admin_logged_in'] = True
            session['admin_id'] = 1
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            # We can also try to look up in the database as a fallback
            user = User.query.filter_by(username=username).first()
            
            # For simplicity, we're assuming admin is user with ID 1
            if user and user.id == 1 and user.check_password(password):
                session['admin_logged_in'] = True
                session['admin_id'] = user.id
                flash('Logged in successfully!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid username or password. Try using Jake/admin123', 'danger')
    
    return render_template('admin/login.html')

@admin_bp.route('/admin/logout')
@admin_login_required
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin.login'))

@admin_bp.route('/admin/messages')
@admin_required
def view_messages():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    filter_type = request.args.get('filter', 'all')
    
    # Base query
    query = ContactMessage.query
    
    # Apply filter if specified
    if filter_type == 'unread':
        query = query.filter_by(is_read=False)
    elif filter_type == 'read':
        query = query.filter_by(is_read=True)
    
    # Get messages with pagination
    messages = query.order_by(
        ContactMessage.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return render_template(
        'admin/messages.html',
        messages=messages
    )

@admin_bp.route('/admin/messages/<int:message_id>')
@admin_required
def view_message(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    
    # Mark as read if not already
    if not message.is_read:
        message.is_read = True
        db.session.commit()
    
    return render_template(
        'admin/message_detail.html',
        message=message
    )

@admin_bp.route('/admin/messages/<int:message_id>/mark_replied', methods=['POST'])
@admin_required
def mark_replied(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    message.is_replied = True
    db.session.commit()
    
    flash('Message marked as replied.', 'success')
    return redirect(url_for('admin.view_message', message_id=message_id))

@admin_bp.route('/admin/dashboard')
@admin_required
def dashboard():
    # Get counts for dashboard
    message_count = ContactMessage.query.count()
    unread_message_count = ContactMessage.query.filter_by(is_read=False).count()
    user_count = User.query.count()
    build_count = Build.query.count()
    
    # Get latest messages
    latest_messages = ContactMessage.query.order_by(
        ContactMessage.created_at.desc()
    ).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        message_count=message_count,
        unread_message_count=unread_message_count,
        user_count=user_count,
        build_count=build_count,
        latest_messages=latest_messages
    )