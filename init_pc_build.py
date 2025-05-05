"""Initialize a pre-configured PC build with components.

This script will pre-select components for all categories in the PC builder
to ensure a complete build is available when users access the builder.
"""

import json
import os
from flask import Flask
from app import app

def add_all_components_to_session():
    """Pre-select all components for the PC builder session."""
    # Create a dictionary to store the configuration
    pc_config = {}
    
    # Component categories
    categories = ['cpu', 'motherboard', 'ram', 'gpu', 'storage', 'power_supply', 'case', 'cooling']
    
    # Load and select the first component from each category
    for category in categories:
        try:
            # Load component data
            with open(f'data/{category}.json', 'r') as f:
                components = json.load(f)
                
            # Select the first component if available
            if components and len(components) > 0:
                pc_config[category] = components[0]['id']
                print(f"Added {category}: {components[0]['name']}")
        except Exception as e:
            print(f"Error adding {category}: {e}")
    
    # Save the configuration to a file for easy loading
    with open('data/default_build.json', 'w') as f:
        json.dump(pc_config, f, indent=2)
    
    print(f"\nDefault build created with {len(pc_config)} components")
    return pc_config

def update_app_route():
    """Add a route to initialize the PC build."""
    @app.route('/init_build')
    def init_build():
        from flask import session, redirect, url_for
        
        # Load the default build
        try:
            with open('data/default_build.json', 'r') as f:
                session['pc_config'] = json.load(f)
        except FileNotFoundError:
            # If the file doesn't exist, create a new build
            session['pc_config'] = add_all_components_to_session()
        
        return redirect(url_for('summary'))
    
    print("Added init_build route to app")

if __name__ == "__main__":
    with app.app_context():
        add_all_components_to_session()
        # Don't update the route here, only when imported
