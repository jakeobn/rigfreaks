from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, ContactMessage, User, Build
from functools import wraps
from auth import login_required
import logging

admin_bp = Blueprint('admin', __name__)

# Admin role required decorator
def admin_required(f):
    @wraps(f)
    @login_required  # First ensure the user is logged in
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        # For simplicity, we're assuming admin is user with ID 1
        # In a real app, you would have a role or is_admin field
        if user and user.id == 1:
            return f(*args, **kwargs)
        else:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
    return decorated_function

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