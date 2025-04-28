from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, send_from_directory
from models import db, ContactMessage, User, Build, PreBuiltConfig
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
import logging
import os
import json
import threading
from datetime import datetime
import time
from chillblast_scraper import ChillblastScraper

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
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find admin user
        user = User.query.filter_by(username=username).first()
        
        # For simplicity, we're assuming admin is user with ID 1
        # In a real app, you would have a role or is_admin field
        if user and user.id == 1 and user.check_password(password):
            session['admin_logged_in'] = True
            session['admin_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
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

# Global variable to track if scraper is running
scraper_running = False
scraper_thread = None

@admin_bp.route('/admin/scraper')
@admin_required
def scraper_dashboard():
    """Display the product scraper dashboard"""
    global scraper_running
    
    # Get the list of scraped files
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_data')
    os.makedirs(data_dir, exist_ok=True)
    
    scraped_files = []
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(data_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        num_products = len(data.get('products', []))
                        
                        # Parse timestamp from filename
                        timestamp_str = filename.split('_')[-2] + '_' + filename.split('_')[-1].split('.')[0]
                        try:
                            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            formatted_timestamp = "Unknown"
                        
                        # Format display name
                        display_name = filename
                        for prefix in ['chillblast_']:
                            if display_name.startswith(prefix):
                                display_name = display_name[len(prefix):]
                        display_name = display_name.split('_')[0].replace('_', ' ').title()
                        
                        scraped_files.append({
                            'filename': filename,
                            'display_name': display_name,
                            'products': num_products,
                            'timestamp': formatted_timestamp
                        })
                except Exception as e:
                    logging.error(f"Error reading file {filename}: {str(e)}")
    
    # Sort files by timestamp (newest first)
    scraped_files.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return render_template(
        'admin/scraper.html',
        scraped_files=scraped_files,
        running=scraper_running,
        message=request.args.get('message'),
        message_category=request.args.get('category', 'info')
    )

@admin_bp.route('/admin/scraper/run', methods=['GET', 'POST'])
@admin_required
def run_scraper():
    """Run the Chillblast scraper"""
    global scraper_running, scraper_thread
    
    if scraper_running:
        return redirect(url_for('admin.scraper_dashboard', 
                              message="Scraper is already running. Please wait for it to finish.",
                              category="warning"))
    
    # If it's a POST request, get parameters from form
    if request.method == 'POST':
        category = request.form.get('category', 'all')
        limit = int(request.form.get('limit', 5))
        
        # Start the scraper in a separate thread
        def run_scraper_thread():
            global scraper_running
            try:
                scraper_running = True
                scraper = ChillblastScraper()
                
                if category == 'all':
                    scraper.scrape_main_categories(limit)
                else:
                    categories = {
                        category: f"https://www.chillblast.com/{category.lower().replace('_', '-')}"
                    }
                    scraper.scrape_categories(categories, limit)
                    
            except Exception as e:
                logging.error(f"Error running scraper: {str(e)}")
            finally:
                scraper_running = False
        
        scraper_thread = threading.Thread(target=run_scraper_thread)
        scraper_thread.daemon = True
        scraper_thread.start()
        
        return redirect(url_for('admin.scraper_dashboard', 
                              message="Scraper started. This may take a few minutes.",
                              category="info"))
    
    # If it's a GET request, just start with default parameters
    def run_default_scraper_thread():
        global scraper_running
        try:
            scraper_running = True
            scraper = ChillblastScraper()
            scraper.scrape_main_categories(3)  # Limit to 3 per category for quick test
        except Exception as e:
            logging.error(f"Error running scraper: {str(e)}")
        finally:
            scraper_running = False
    
    scraper_thread = threading.Thread(target=run_default_scraper_thread)
    scraper_thread.daemon = True
    scraper_thread.start()
    
    return redirect(url_for('admin.scraper_dashboard', 
                          message="Scraper started with default settings (3 products per category).",
                          category="info"))

@admin_bp.route('/admin/scraper/view/<filename>')
@admin_required
def view_scraped_file(filename):
    """View the contents of a scraped file"""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_data')
    file_path = os.path.join(data_dir, filename)
    
    if not os.path.exists(file_path):
        flash("File not found.", "danger")
        return redirect(url_for('admin.scraper_dashboard'))
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            products = data.get('products', [])
        
        return render_template(
            'admin/view_scraped_file.html',
            products=products,
            filename=filename
        )
    except Exception as e:
        flash(f"Error reading file: {str(e)}", "danger")
        return redirect(url_for('admin.scraper_dashboard'))

@admin_bp.route('/admin/scraper/import/<filename>')
@admin_required
def import_products(filename):
    """Import products from a scraped file into the database"""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_data')
    file_path = os.path.join(data_dir, filename)
    
    if not os.path.exists(file_path):
        flash("File not found.", "danger")
        return redirect(url_for('admin.scraper_dashboard'))
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            products = data.get('products', [])
        
        # Import products as prebuilt configurations
        counter = 0
        for product in products:
            # Skip products without sufficient data
            if not product.get('title') or not product.get('price'):
                continue
                
            # Map product category to our system
            category_mapping = {
                'Gaming_PCs': 'gaming',
                'Custom_PCs': 'custom',
                'Workstations': 'workstation'
            }
            category = category_mapping.get(product.get('category'), 'gaming')
            
            # Create a new prebuilt config
            prebuilt = PreBuiltConfig(
                name=product.get('title'),
                description=product.get('description', ''),
                category=category,
                price=product.get('price'),
                cpu_id=product.get('components', {}).get('cpu', ''),
                gpu_id=product.get('components', {}).get('gpu', ''),
                ram_id=product.get('components', {}).get('ram', ''),
                storage_id=product.get('components', {}).get('storage', ''),
                motherboard_id=product.get('components', {}).get('motherboard', ''),
                power_supply_id=product.get('components', {}).get('power_supply', ''),
                case_id=product.get('components', {}).get('case', ''),
                cooling_id=product.get('components', {}).get('cooling', '')
            )
            
            db.session.add(prebuilt)
            counter += 1
        
        db.session.commit()
        flash(f"Successfully imported {counter} products as pre-built configurations.", "success")
        return redirect(url_for('admin.scraper_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error importing products: {str(e)}", "danger")
        return redirect(url_for('admin.scraper_dashboard'))

@admin_bp.route('/admin/scraper/import_single/<filename>/<int:product_index>')
@admin_required
def import_single_product(filename, product_index):
    """Import a single product from a scraped file"""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_data')
    file_path = os.path.join(data_dir, filename)
    
    if not os.path.exists(file_path):
        flash("File not found.", "danger")
        return redirect(url_for('admin.scraper_dashboard'))
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            products = data.get('products', [])
            
            if product_index >= len(products):
                flash("Product index out of range.", "danger")
                return redirect(url_for('admin.view_scraped_file', filename=filename))
            
            product = products[product_index]
            
            # Map product category to our system
            category_mapping = {
                'Gaming_PCs': 'gaming',
                'Custom_PCs': 'custom',
                'Workstations': 'workstation'
            }
            category = category_mapping.get(product.get('category'), 'gaming')
            
            # Create a new prebuilt config
            prebuilt = PreBuiltConfig(
                name=product.get('title'),
                description=product.get('description', ''),
                category=category,
                price=product.get('price'),
                cpu_id=product.get('components', {}).get('cpu', ''),
                gpu_id=product.get('components', {}).get('gpu', ''),
                ram_id=product.get('components', {}).get('ram', ''),
                storage_id=product.get('components', {}).get('storage', ''),
                motherboard_id=product.get('components', {}).get('motherboard', ''),
                power_supply_id=product.get('components', {}).get('power_supply', ''),
                case_id=product.get('components', {}).get('case', ''),
                cooling_id=product.get('components', {}).get('cooling', '')
            )
            
            db.session.add(prebuilt)
            db.session.commit()
            
            flash(f"Successfully imported '{product.get('title')}' as a pre-built configuration.", "success")
            return redirect(url_for('admin.view_scraped_file', filename=filename))
            
    except Exception as e:
        db.session.rollback()
        flash(f"Error importing product: {str(e)}", "danger")
        return redirect(url_for('admin.view_scraped_file', filename=filename))