import json
import functools
import time

# Cache for component data and compatibility rules
_component_cache = {'data': None, 'timestamp': 0}
_rules_cache = {'data': None, 'timestamp': 0}
CACHE_LIFETIME = 300  # Cache lifetime in seconds (5 minutes)

# Load component data with caching
def load_component_data():
    current_time = time.time()
    if _component_cache['data'] is None or current_time - _component_cache['timestamp'] > CACHE_LIFETIME:
        with open('static/data/components.json', 'r') as f:
            _component_cache['data'] = json.load(f)
            _component_cache['timestamp'] = current_time
    return _component_cache['data']

# Load compatibility rules with caching
def load_compatibility_rules():
    current_time = time.time()
    if _rules_cache['data'] is None or current_time - _rules_cache['timestamp'] > CACHE_LIFETIME:
        with open('static/data/compatibility_rules.json', 'r') as f:
            _rules_cache['data'] = json.load(f)
            _rules_cache['timestamp'] = current_time
    return _rules_cache['data']

# Helper function to get component data by ID efficiently 
def get_component_by_id(components, category, component_id):
    if category not in components or not component_id:
        return None
    return next((c for c in components[category] if c['id'] == component_id), None)

# Check if components are compatible with optimized lookups
def check_compatibility(config):
    # No components selected yet
    if not config:
        return []
    
    issues = []
    rules = load_compatibility_rules()
    components = load_component_data()
    
    # Create a lookup dictionary for quick access to selected components
    selected = {}
    for category, component_id in config.items():
        selected[category] = get_component_by_id(components, category, component_id)
    
    # CPU and motherboard socket compatibility
    if 'cpu' in selected and 'motherboard' in selected:
        cpu_data = selected['cpu']
        mobo_data = selected['motherboard']
        if cpu_data and mobo_data and cpu_data['socket'] != mobo_data['socket']:
            issues.append(f"CPU socket ({cpu_data['socket']}) is not compatible with motherboard socket ({mobo_data['socket']})")
    
    # RAM compatibility with motherboard
    if 'ram' in selected and 'motherboard' in selected:
        ram_data = selected['ram']
        mobo_data = selected['motherboard']
        if ram_data and mobo_data and ram_data['type'] != mobo_data['ram_type']:
            issues.append(f"RAM type ({ram_data['type']}) is not compatible with motherboard ({mobo_data['ram_type']})")
    
    # Power supply wattage check
    if 'power_supply' in selected:
        power_data = selected['power_supply']
        required_power = 150  # Base power for other components
        
        # Add CPU power requirements
        if 'cpu' in selected and selected['cpu']:
            required_power += selected['cpu'].get('tdp', 0)
        
        # Add GPU power requirements
        if 'gpu' in selected and selected['gpu']:
            required_power += selected['gpu'].get('tdp', 0)
        
        if power_data and power_data['wattage'] < required_power:
            issues.append(f"Power supply ({power_data['wattage']}W) is insufficient for the selected components (estimated {required_power}W required)")
    
    # Case compatibility check
    if 'case' in selected and 'motherboard' in selected:
        case_data = selected['case']
        mobo_data = selected['motherboard']
        if case_data and mobo_data and case_data['form_factor'] != mobo_data['form_factor']:
            issues.append(f"Case form factor ({case_data['form_factor']}) does not support motherboard form factor ({mobo_data['form_factor']})")
    
    return issues

# Calculate total price with optimized component lookup
def calculate_total_price(config):
    if not config:
        return 0
        
    components = load_component_data()
    total = 0
    
    for category, component_id in config.items():
        component = get_component_by_id(components, category, component_id)
        if component:
            total += component.get('price', 0)
    
    return total