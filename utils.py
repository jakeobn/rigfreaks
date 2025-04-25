import json

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