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
from content_scraper import ContentScraper, run_content_scraper

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
    """Run the Content Aggregator scraper for PC components"""
    global scraper_running, scraper_thread
    
    if scraper_running:
        return redirect(url_for('admin.scraper_dashboard', 
                              message="Scraper is already running. Please wait for it to finish.",
                              category="warning"))
    
    # If it's a POST request, get parameters from form
    if request.method == 'POST':
        category = request.form.get('category', 'all')
        limit = int(request.form.get('limit', 5))
        get_details = request.form.get('get_details') == 'on'
        
        # Start the scraper in a separate thread
        def run_scraper_thread():
            global scraper_running
            try:
                scraper_running = True
                search_terms = {
                    "cpu": "processor intel amd",
                    "gpu": "graphics card nvidia amd",
                    "motherboard": "motherboard",
                    "memory": "ram ddr4 ddr5",
                    "storage": "ssd nvme",
                    "case": "computer case",
                    "power_supply": "power supply",
                    "cpu_cooler": "cpu cooler"
                }
                
                if category == 'all':
                    # Fetch all categories
                    filepath = run_content_scraper(categories=None, 
                                                 search_terms=search_terms, 
                                                 count_per_category=limit)
                else:
                    # Fetch specific category
                    filepath = run_content_scraper(categories=[category], 
                                                 search_terms=search_terms, 
                                                 count_per_category=limit)
                    
                logging.info(f"Scraper completed. Data saved to {filepath}")
                    
            except Exception as e:
                logging.error(f"Error running scraper: {str(e)}")
            finally:
                scraper_running = False
        
        scraper_thread = threading.Thread(target=run_scraper_thread)
        scraper_thread.daemon = True
        scraper_thread.start()
        
        return redirect(url_for('admin.scraper_dashboard', 
                              message="Content Aggregator scraper started. This may take a few minutes.",
                              category="info"))
    
    # If it's a GET request, just start with default parameters
    def run_default_scraper_thread():
        global scraper_running
        try:
            scraper_running = True
            # Just fetch the most common categories with minimal details
            common_categories = ['cpu', 'gpu', 'memory', 'storage', 'motherboard']
            filepath = run_content_scraper(categories=common_categories, count_per_category=3)
            logging.info(f"Scraper completed. Data saved to {filepath}")
        except Exception as e:
            logging.error(f"Error running scraper: {str(e)}")
        finally:
            scraper_running = False
    
    scraper_thread = threading.Thread(target=run_default_scraper_thread)
    scraper_thread.daemon = True
    scraper_thread.start()
    
    return redirect(url_for('admin.scraper_dashboard', 
                          message="Content Aggregator scraper started with default settings (common components, 3 products each).",
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
            
            # Check if it's PCPartPicker format (has 'categories') or old format (has 'products')
            all_products = []
            source = data.get('source', 'Unknown')
            
            if 'categories' in data:
                # New PCPartPicker format
                categories = data.get('categories', {})
                for category_name, products in categories.items():
                    # Add category info to each product
                    for product in products:
                        product['category'] = category_name
                        all_products.append(product)
            else:
                # Old format
                all_products = data.get('products', [])
        
        return render_template(
            'admin/view_scraped_file.html',
            products=all_products,
            filename=filename,
            source=source
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
            
            # Prepare all products from any file format
            all_products = []
            
            # Check if it's PCPartPicker format (has 'categories') or old format (has 'products')
            if 'categories' in data:
                # New PCPartPicker format
                categories = data.get('categories', {})
                for category_name, products in categories.items():
                    # Add category info to each product
                    for product in products:
                        product['category'] = category_name
                        all_products.append(product)
            else:
                # Old format
                all_products = data.get('products', [])
        
        # Import products as prebuilt configurations
        counter = 0
        for product in all_products:
            # Skip products without sufficient data
            product_name = product.get('name') or product.get('title')
            product_price = product.get('price')
            
            if not product_name or not product_price:
                continue
                
            # Map product category to our system
            category_mapping = {
                # PCPartPicker categories
                'cpu': 'processor',
                'motherboard': 'motherboard',
                'memory': 'memory',
                'storage': 'storage',
                'gpu': 'graphics',
                'case': 'case',
                'power_supply': 'power',
                'cpu_cooler': 'cooling',
                
                # Old Chillblast categories
                'Gaming_PCs': 'gaming',
                'Custom_PCs': 'custom',
                'Workstations': 'workstation'
            }
            
            product_category = product.get('category', 'unknown')
            category = category_mapping.get(product_category, 'custom')
            
            # Get the description from most likely fields
            description = product.get('description', '')
            if not description and product.get('specifications'):
                # Format specifications as description if no description available
                specs = product.get('specifications', {})
                description = "\\n".join([f"{key}: {value}" for key, value in specs.items()])
            
            # Extract component IDs based on the format
            cpu_id = ''
            gpu_id = ''
            memory_id = ''
            storage_id = ''
            motherboard_id = ''
            power_supply_id = ''
            case_id = ''
            cooling_id = ''
            
            # For PCPartPicker data
            if product_category == 'cpu':
                cpu_id = product_name
            elif product_category == 'gpu':
                gpu_id = product_name
            elif product_category == 'memory':
                memory_id = product_name
            elif product_category == 'storage':
                storage_id = product_name
            elif product_category == 'motherboard':
                motherboard_id = product_name
            elif product_category == 'power_supply':
                power_supply_id = product_name
            elif product_category == 'case':
                case_id = product_name
            elif product_category == 'cpu_cooler':
                cooling_id = product_name
            # For old format (Chillblast)
            elif 'components' in product:
                components = product.get('components', {})
                cpu_id = components.get('cpu', '')
                gpu_id = components.get('gpu', '')
                memory_id = components.get('ram', '')
                storage_id = components.get('storage', '')
                motherboard_id = components.get('motherboard', '')
                power_supply_id = components.get('power_supply', '')
                case_id = components.get('case', '')
                cooling_id = components.get('cooling', '')
            
            # Create a new prebuilt config
            prebuilt = PreBuiltConfig(
                name=product_name,
                description=description,
                category=category,
                price=float(product_price) if isinstance(product_price, str) else product_price,
                cpu_id=cpu_id,
                gpu_id=gpu_id,
                ram_id=memory_id,
                storage_id=storage_id,
                motherboard_id=motherboard_id,
                power_supply_id=power_supply_id,
                case_id=case_id,
                cooling_id=cooling_id
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
            
            # Prepare all products from any file format
            all_products = []
            
            # Check if it's PCPartPicker format (has 'categories') or old format (has 'products')
            if 'categories' in data:
                # New PCPartPicker format
                categories = data.get('categories', {})
                for category_name, products in categories.items():
                    # Add category info to each product
                    for product in products:
                        product['category'] = category_name
                        all_products.append(product)
            else:
                # Old format
                all_products = data.get('products', [])
            
            if product_index >= len(all_products):
                flash("Product index out of range.", "danger")
                return redirect(url_for('admin.view_scraped_file', filename=filename))
            
            product = all_products[product_index]
            
            # Skip products without sufficient data
            product_name = product.get('name') or product.get('title')
            product_price = product.get('price')
            
            if not product_name or not product_price:
                flash("Product doesn't have required name and price information.", "danger")
                return redirect(url_for('admin.view_scraped_file', filename=filename))
                
            # Map product category to our system
            category_mapping = {
                # PCPartPicker categories
                'cpu': 'processor',
                'motherboard': 'motherboard',
                'memory': 'memory',
                'storage': 'storage',
                'gpu': 'graphics',
                'case': 'case',
                'power_supply': 'power',
                'cpu_cooler': 'cooling',
                
                # Old Chillblast categories
                'Gaming_PCs': 'gaming',
                'Custom_PCs': 'custom',
                'Workstations': 'workstation'
            }
            
            product_category = product.get('category', 'unknown')
            category = category_mapping.get(product_category, 'custom')
            
            # Get the description from most likely fields
            description = product.get('description', '')
            if not description and product.get('specifications'):
                # Format specifications as description if no description available
                specs = product.get('specifications', {})
                description = "\\n".join([f"{key}: {value}" for key, value in specs.items()])
            
            # Extract component IDs based on the format
            cpu_id = ''
            gpu_id = ''
            memory_id = ''
            storage_id = ''
            motherboard_id = ''
            power_supply_id = ''
            case_id = ''
            cooling_id = ''
            
            # For PCPartPicker data
            if product_category == 'cpu':
                cpu_id = product_name
            elif product_category == 'gpu':
                gpu_id = product_name
            elif product_category == 'memory':
                memory_id = product_name
            elif product_category == 'storage':
                storage_id = product_name
            elif product_category == 'motherboard':
                motherboard_id = product_name
            elif product_category == 'power_supply':
                power_supply_id = product_name
            elif product_category == 'case':
                case_id = product_name
            elif product_category == 'cpu_cooler':
                cooling_id = product_name
            # For old format (Chillblast)
            elif 'components' in product:
                components = product.get('components', {})
                cpu_id = components.get('cpu', '')
                gpu_id = components.get('gpu', '')
                memory_id = components.get('ram', '')
                storage_id = components.get('storage', '')
                motherboard_id = components.get('motherboard', '')
                power_supply_id = components.get('power_supply', '')
                case_id = components.get('case', '')
                cooling_id = components.get('cooling', '')
            
            # Create a new prebuilt config
            prebuilt = PreBuiltConfig(
                name=product_name,
                description=description,
                category=category,
                price=float(product_price) if isinstance(product_price, str) else product_price,
                cpu_id=cpu_id,
                gpu_id=gpu_id,
                ram_id=memory_id,
                storage_id=storage_id,
                motherboard_id=motherboard_id,
                power_supply_id=power_supply_id,
                case_id=case_id,
                cooling_id=cooling_id
            )
            
            db.session.add(prebuilt)
            db.session.commit()
            
            flash(f"Successfully imported '{product_name}' as a pre-built configuration.", "success")
            return redirect(url_for('admin.view_scraped_file', filename=filename))
            
    except Exception as e:
        db.session.rollback()
        flash(f"Error importing product: {str(e)}", "danger")
        return redirect(url_for('admin.view_scraped_file', filename=filename))