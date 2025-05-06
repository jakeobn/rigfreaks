import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, make_response
from models import db, User, Build, PreBuiltConfig, ContactMessage
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from utils import load_component_data, load_compatibility_rules, check_compatibility, calculate_total_price

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-key-for-testing")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database with optimized connection settings
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,  # Recycle connections every 5 minutes
    "pool_pre_ping": True,  # Verify connections before using them
    "pool_size": 10,  # Set pool size for better resource management
    "max_overflow": 15,  # Allow up to 15 additional connections when pool is full
    "pool_timeout": 30,  # Wait up to 30 seconds for a connection from the pool
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable event system for better performance

# Initialize the database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()
    
# Register blueprints
from auth import auth_bp
from builds import builds_bp
from admin import admin_bp
from cart import cart_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(builds_bp, url_prefix='/builds')
app.register_blueprint(admin_bp)
app.register_blueprint(cart_bp)

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    
    if search_query:
        # In a real implementation, this would search the database
        # For now, we'll just pass the search query to the template
        return render_template('index.html', search_query=search_query)
    
    return render_template('index.html')

@app.route('/builder', methods=['GET', 'POST'])
def builder():
    # Redirect to the step-by-step builder as the default PC builder
    return redirect(url_for('step_builder'))

@app.route('/builder/classic', methods=['GET', 'POST'])
def classic_builder():
    # Initialize session if it doesn't exist
    if 'pc_config' not in session:
        session['pc_config'] = {}
    
    components = load_component_data()
    compatibility_issues = check_compatibility(session['pc_config'])
    total_price = calculate_total_price(session['pc_config'])
    
    return render_template(
        'builder.html',
        components=components,
        current_config=session['pc_config'],
        compatibility_issues=compatibility_issues,
        total_price=total_price
    )

@app.route('/builder/step-by-step', methods=['GET'])
def step_builder():
    """Step-by-Step PC Builder page with guided interface."""
    # Initialize session if it doesn't exist
    if 'pc_config' not in session:
        session['pc_config'] = {}
    
    components = load_component_data()
    compatibility_issues = check_compatibility(session['pc_config'])
    total_price = calculate_total_price(session['pc_config'])
    
    return render_template(
        'step_builder.html',
        components=components,
        current_config=session['pc_config'],
        compatibility_issues=compatibility_issues,
        total_price=total_price
    )

@app.route('/select/<category>', methods=['GET'])
def select_component(category):
    components = load_component_data()
    
    if category not in components:
        flash(f"Component category '{category}' not found", "danger")
        return redirect(url_for('step_builder'))
    
    # Get the current configuration
    current_config = session.get('pc_config', {})
    
    return render_template(
        'component_select.html',
        category=category,
        components=components[category],
        current_selection=current_config.get(category)
    )
    
@app.route('/component/<category>/<component_id>', methods=['GET'])
def component_detail(category, component_id):
    components = load_component_data()
    
    if category not in components:
        flash(f"Component category '{category}' not found", "danger")
        return redirect(url_for('step_builder'))
    
    # Use the helper function for more efficient lookup
    from utils import get_component_by_id
    component = get_component_by_id(components, category, component_id)
    
    if not component:
        flash(f"Component with ID '{component_id}' not found in category '{category}'", "danger")
        return redirect(url_for('select_component', category=category))
    
    # Check if this component is currently selected in the build
    current_config = session.get('pc_config', {})
    is_selected = current_config.get(category) == component_id
    
    # Add cache control headers for better client-side caching
    response = make_response(render_template(
        'component_details.html',
        category=category,
        component=component,
        is_selected=is_selected
    ))
    response.headers['Cache-Control'] = 'private, max-age=60'  # Cache for 60 seconds
    return response

@app.route('/add/<category>/<component_id>', methods=['POST'])
def add_component(category, component_id):
    app.logger.debug(f"Adding/Removing component: {category} - {component_id}")
    # Initialize configuration if it doesn't exist
    if 'pc_config' not in session:
        session['pc_config'] = {}
    
    # Toggle component behavior - if the same component is selected, remove it
    if category in session['pc_config'] and session['pc_config'][category] == component_id:
        # This is a toggle/unselect action
        del session['pc_config'][category]
        session.modified = True
        return redirect(url_for('step_builder'))
    else:
        # This is an add/select action
        # Add component to configuration
        session['pc_config'][category] = component_id
        session.modified = True
        
        # Check compatibility after adding component
        compatibility_issues = check_compatibility(session['pc_config'])
        if compatibility_issues:
            flash_message = "<strong>Warning:</strong> Compatibility issues detected:<ul>"
            for issue in compatibility_issues:
                flash_message += f"<li>{issue}</li>"
            flash_message += "</ul>"
            flash(flash_message, "warning")
    
    return redirect(url_for('step_builder'))

@app.route('/remove/<category>', methods=['POST'])
def remove_component(category):
    if 'pc_config' in session and category in session['pc_config']:
        del session['pc_config'][category]
        session.modified = True
    
    return redirect(url_for('step_builder'))

@app.route('/summary')
def summary():
    if 'pc_config' not in session or not session['pc_config']:
        flash("Please build a PC configuration first", "warning")
        return redirect(url_for('step_builder'))
    
    components = load_component_data()
    config_details = {}
    
    # More efficient component lookup using the helper function
    for category, component_id in session['pc_config'].items():
        from utils import get_component_by_id
        component = get_component_by_id(components, category, component_id)
        if component:
            config_details[category] = component
    
    compatibility_issues = check_compatibility(session['pc_config'])
    total_price = calculate_total_price(session['pc_config'])
    
    # Get performance benchmarks if CPU and GPU are selected
    performance_summary = None
    if 'cpu' in session['pc_config'] and 'gpu' in session['pc_config']:
        try:
            # Lazy import for better performance
            from benchmarks import get_performance_summary
            performance_summary = get_performance_summary(session['pc_config'])
        except Exception as e:
            app.logger.error(f"Error retrieving performance summary: {str(e)}")
    
    # Cache control headers for better browser caching
    response = make_response(render_template(
        'summary.html',
        config=config_details,
        compatibility_issues=compatibility_issues,
        total_price=total_price,
        performance=performance_summary
    ))
    response.headers['Cache-Control'] = 'private, max-age=10'  # Cache for 10 seconds
    return response

# Benchmarks and compare routes removed as per updated site map

@app.route('/api/check_compatibility', methods=['POST'])
def api_check_compatibility():
    config = request.json.get('config', {})
    issues = check_compatibility(config)
    return jsonify({
        'compatible': len(issues) == 0,
        'issues': issues
    })

@app.route('/api/calculate_price', methods=['POST'])
def api_calculate_price():
    config = request.json.get('config', {})
    total_price = calculate_total_price(config)
    return jsonify({
        'total': total_price
    })

@app.route('/reset', methods=['POST'])
def reset_configuration():
    if 'pc_config' in session:
        session['pc_config'] = {}
        session.modified = True
    
    return redirect(url_for('step_builder'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        category = request.form.get('category')
        message = request.form.get('message')
        
        # Validate required fields
        if not all([name, email, message]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('contact.html')
            
        try:
            # Create new contact message
            contact_message = ContactMessage(
                name=name,
                email=email,
                subject=subject,
                category=category,
                message=message,
                user_id=session.get('user_id')  # Link to user if logged in
            )
            
            # Save to database
            db.session.add(contact_message)
            db.session.commit()
            
            # Log the contact submission
            app.logger.info(f'Contact form submission saved: ID {contact_message.id} from {name} ({email})')
            
            # Show success message
            flash('Thank you for contacting us! We will get back to you shortly.', 'success')
        except Exception as e:
            # Log the error and show error message
            app.logger.error(f'Error saving contact form: {str(e)}')
            db.session.rollback()
            flash('There was an error processing your request. Please try again later.', 'danger')
            
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

# Legal routes
@app.route('/terms')
def terms():
    """Terms & Conditions page."""
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    """Privacy Policy page."""
    return render_template('privacy.html')

@app.route('/cookies')
def cookies():
    """Cookie Policy page."""
    return render_template('cookies.html')

@app.route('/about')
def about():
    """About Us page with company information."""
    return render_template('about.html')

@app.route('/delivery')
def delivery():
    """Delivery Information page with shipping details."""
    return render_template('delivery.html')

@app.route('/faq')
def faq():
    """Frequently Asked Questions page."""
    return render_template('faq.html')

@app.route('/sitemap')
def sitemap():
    """Site Map page showing all website pages in an organized format."""
    return render_template('sitemap.html')


@app.route('/prebuilt')
def prebuilt_redirect():
    """Redirect to the prebuilt configurations page."""
    return redirect(url_for('builds.prebuilt_configs'))

@app.route('/product/<int:config_id>')
def product_detail(config_id):
    """Product detail page for a specific prebuilt configuration."""
    # Get the prebuilt configuration
    try:
        config = PreBuiltConfig.query.get_or_404(config_id)
        
        # Load component details
        components = load_component_data()
    except Exception as e:
        app.logger.error(f"Error loading product with ID {config_id}: {str(e)}")
        flash('The requested product could not be found.', 'error')
        return redirect(url_for('builds.prebuilt_configs'))
    config_details = {}
    
    # Get component details for each category
    for category in ['cpu', 'motherboard', 'ram', 'gpu', 'storage', 'power_supply', 'case', 'cooling']:
        component_id = getattr(config, f'{category}_id')
        if component_id:
            category_components = components.get(category, [])
            component = next((c for c in category_components if c['id'] == component_id), None)
            if component:
                config_details[category] = component
    
    # Calculate performance benchmarks
    performance_summary = None
    if config.cpu_id and config.gpu_id:
        try:
            # Lazy import for better performance
            from benchmarks import get_performance_summary
            temp_config = {
                'cpu': config.cpu_id,
                'gpu': config.gpu_id,
                'ram': config.ram_id
            }
            performance_summary = get_performance_summary(temp_config)
        except Exception as e:
            app.logger.error(f"Error retrieving performance summary: {str(e)}")
    
    # Check compatibility
    temp_config = {}
    for category in ['cpu', 'motherboard', 'ram', 'gpu', 'storage', 'power_supply', 'case', 'cooling']:
        component_id = getattr(config, f'{category}_id')
        if component_id:
            temp_config[category] = component_id
            
    compatibility_issues = check_compatibility(temp_config)
    
    # Use specialized template for the Ryzen 5 5500 RTX 4060 product
    if config.name == "Ryzen 5 5500 RTX 4060 Gaming PC":
        return render_template(
            'product_detail_ryzen.html',
            config=config,
            config_details=config_details,
            performance=performance_summary,
            compatibility_issues=compatibility_issues,
            PreBuiltConfig=PreBuiltConfig
        )
    else:
        return render_template(
            'product_detail.html',
            config=config,
            config_details=config_details,
            performance=performance_summary,
            compatibility_issues=compatibility_issues,
            PreBuiltConfig=PreBuiltConfig
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
