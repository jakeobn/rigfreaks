import os
import json
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-key-for-testing")

# Load component data
def load_component_data():
    with open('static/data/components.json', 'r') as f:
        return json.load(f)

# Load compatibility rules
def load_compatibility_rules():
    with open('static/data/compatibility_rules.json', 'r') as f:
        return json.load(f)

# Check if components are compatible
def check_compatibility(config):
    rules = load_compatibility_rules()
    issues = []
    
    # No components selected yet
    if not config:
        return []
    
    components = load_component_data()
    
    # Example compatibility check: CPU and motherboard socket compatibility
    if 'cpu' in config and 'motherboard' in config:
        cpu_data = next((c for c in components['cpu'] if c['id'] == config['cpu']), None)
        mobo_data = next((m for m in components['motherboard'] if m['id'] == config['motherboard']), None)
        
        if cpu_data and mobo_data and cpu_data['socket'] != mobo_data['socket']:
            issues.append(f"CPU socket ({cpu_data['socket']}) is not compatible with motherboard socket ({mobo_data['socket']})")
    
    # RAM compatibility with motherboard
    if 'ram' in config and 'motherboard' in config:
        ram_data = next((r for r in components['ram'] if r['id'] == config['ram']), None)
        mobo_data = next((m for m in components['motherboard'] if m['id'] == config['motherboard']), None)
        
        if ram_data and mobo_data and ram_data['type'] != mobo_data['ram_type']:
            issues.append(f"RAM type ({ram_data['type']}) is not compatible with motherboard ({mobo_data['ram_type']})")
    
    # Power supply wattage check
    if 'power_supply' in config:
        power_data = next((p for p in components['power_supply'] if p['id'] == config['power_supply']), None)
        required_power = 0
        
        # Calculate power requirements based on components
        if 'cpu' in config:
            cpu_data = next((c for c in components['cpu'] if c['id'] == config['cpu']), None)
            if cpu_data:
                required_power += cpu_data.get('tdp', 0)
        
        if 'gpu' in config:
            gpu_data = next((g for g in components['gpu'] if g['id'] == config['gpu']), None)
            if gpu_data:
                required_power += gpu_data.get('tdp', 0)
        
        # Add base power for other components
        required_power += 150  # Base power for other components
        
        if power_data and power_data['wattage'] < required_power:
            issues.append(f"Power supply ({power_data['wattage']}W) is insufficient for the selected components (estimated {required_power}W required)")
    
    # Case compatibility check
    if 'case' in config and 'motherboard' in config:
        case_data = next((c for c in components['case'] if c['id'] == config['case']), None)
        mobo_data = next((m for m in components['motherboard'] if m['id'] == config['motherboard']), None)
        
        if case_data and mobo_data and case_data['form_factor'] != mobo_data['form_factor']:
            issues.append(f"Case form factor ({case_data['form_factor']}) does not support motherboard form factor ({mobo_data['form_factor']})")
    
    return issues

# Calculate total price
def calculate_total_price(config):
    if not config:
        return 0
        
    components = load_component_data()
    total = 0
    
    for category, component_id in config.items():
        category_components = components.get(category, [])
        component = next((c for c in category_components if c['id'] == component_id), None)
        if component:
            total += component.get('price', 0)
    
    return total

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
