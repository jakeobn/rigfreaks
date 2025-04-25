import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, User, Build, PreBuiltConfig, ContactMessage
from werkzeug.middleware.proxy_fix import ProxyFix
from utils import load_component_data, load_compatibility_rules, check_compatibility, calculate_total_price

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-key-for-testing")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()
    
# Register blueprints
from auth import auth_bp
from builds import builds_bp
from admin import admin_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(builds_bp, url_prefix='/builds')
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/builder', methods=['GET', 'POST'])
def builder():
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

@app.route('/select/<category>', methods=['GET'])
def select_component(category):
    components = load_component_data()
    
    if category not in components:
        flash(f"Component category '{category}' not found", "danger")
        return redirect(url_for('builder'))
    
    # Get the current configuration
    current_config = session.get('pc_config', {})
    
    return render_template(
        'component_select.html',
        category=category,
        components=components[category],
        current_selection=current_config.get(category)
    )

@app.route('/add/<category>/<component_id>', methods=['POST'])
def add_component(category, component_id):
    # Initialize configuration if it doesn't exist
    if 'pc_config' not in session:
        session['pc_config'] = {}
    
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
    
    return redirect(url_for('builder'))

@app.route('/remove/<category>', methods=['POST'])
def remove_component(category):
    if 'pc_config' in session and category in session['pc_config']:
        del session['pc_config'][category]
        session.modified = True
    
    return redirect(url_for('builder'))

@app.route('/summary')
def summary():
    if 'pc_config' not in session or not session['pc_config']:
        flash("Please build a PC configuration first", "warning")
        return redirect(url_for('builder'))
    
    components = load_component_data()
    config_details = {}
    
    for category, component_id in session['pc_config'].items():
        category_components = components.get(category, [])
        component = next((c for c in category_components if c['id'] == component_id), None)
        if component:
            config_details[category] = component
    
    compatibility_issues = check_compatibility(session['pc_config'])
    total_price = calculate_total_price(session['pc_config'])
    
    return render_template(
        'summary.html',
        config=config_details,
        compatibility_issues=compatibility_issues,
        total_price=total_price
    )

@app.route('/compare/<category>')
def compare_components(category):
    components = load_component_data()
    
    if category not in components:
        flash(f"Component category '{category}' not found", "danger")
        return redirect(url_for('builder'))
    
    return render_template(
        'compare.html',
        category=category,
        components=components[category]
    )

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
    
    return redirect(url_for('builder'))

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

@app.route('/terms')
def terms():
    return render_template('legal/terms.html')

@app.route('/privacy')
def privacy():
    return render_template('legal/privacy.html')

@app.route('/returns')
def returns():
    return render_template('legal/returns.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
