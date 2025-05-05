"""Import Chillblast component data into the application's component database.

This script imports component data scraped from Chillblast into our application's
component data files. It maps the scraped data to our internal component format.
"""

import os
import json
import glob
from datetime import datetime

# Directory where scraped data is stored
DATA_DIR = "scraped_data"

# Directory where our component data is stored
COMPONENT_DATA_DIR = "data"

def find_latest_components_file():
    """Find the most recent chillblast_components_*.json file."""
    pattern = os.path.join(DATA_DIR, "chillblast_components_*.json")
    files = glob.glob(pattern)
    if not files:
        return None
    
    # Sort by modification time, newest first
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

def load_existing_components(category):
    """Load existing component data from our data directory."""
    filepath = os.path.join(COMPONENT_DATA_DIR, f"{category}.json")
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading {filepath}, creating new file")
            return []

def map_component(comp_data, category, start_id=1000):
    """Map Chillblast component data to our internal format."""
    # Base component structure
    component = {
        "id": str(start_id),
        "name": comp_data.get("name", "Unknown Component"),
        "brand": comp_data.get("brand", "Chillblast"),
        "price": comp_data.get("price", 0),
        "description": comp_data.get("description", ""),
        "specs": {},
        "image": comp_data.get("image_url", ""),
        "source": "chillblast"
    }
    
    # Extract specs from the detailed product data if available
    if "specifications" in comp_data:
        specs = comp_data["specifications"]
        component["specs"] = specs
        
        # Add specific attributes based on component type
        if category == "cpu":
            component["socket"] = specs.get("Socket", "")
            component["cores"] = specs.get("Cores", "")
            component["clock_speed"] = specs.get("Clock Speed", "")
        elif category == "motherboard":
            component["socket"] = specs.get("Socket", "")
            component["form_factor"] = specs.get("Form Factor", "ATX")
            component["chipset"] = specs.get("Chipset", "")
        elif category == "ram":
            component["capacity"] = specs.get("Capacity", "")
            component["speed"] = specs.get("Speed", "")
            component["type"] = specs.get("Type", "DDR4")
        elif category == "gpu":
            component["vram"] = specs.get("Memory", "")
            component["core_clock"] = specs.get("Core Clock", "")
        elif category == "storage":
            component["capacity"] = specs.get("Capacity", "")
            component["type"] = specs.get("Type", "SSD")
            component["interface"] = specs.get("Interface", "")
        elif category == "power_supply":
            component["wattage"] = specs.get("Wattage", "")
            component["efficiency"] = specs.get("Efficiency", "")
            component["modular"] = "modular" in (specs.get("Type", "").lower() or "")
        elif category == "case":
            component["form_factor"] = specs.get("Form Factor", "Mid Tower")
            component["color"] = specs.get("Color", "Black")
        elif category == "cooling":
            component["type"] = specs.get("Type", "Air")
            component["size"] = specs.get("Size", "")
    
    return component

def import_components(components_data):
    """Import component data from Chillblast into our application."""
    results = {}
    
    for category, items in components_data.items():
        print(f"Importing {len(items)} {category} components...")
        
        # Load existing components
        existing_components = load_existing_components(category)
        existing_ids = set(int(comp["id"]) for comp in existing_components if comp["id"].isdigit())
        
        # Find the next available ID
        next_id = 1000
        if existing_ids:
            next_id = max(existing_ids) + 1
        
        # Map and add new components
        new_components = []
        for i, item in enumerate(items):
            component = map_component(item, category, next_id + i)
            new_components.append(component)
        
        # Combine with existing components
        combined_components = existing_components + new_components
        
        # Save to our component data file
        output_path = os.path.join(COMPONENT_DATA_DIR, f"{category}.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(combined_components, f, indent=2)
        
        results[category] = {
            "existing": len(existing_components),
            "new": len(new_components),
            "total": len(combined_components)
        }
    
    return results

def main():
    """Main function to run the component import process."""
    print("Starting Chillblast component import...")
    
    # Find latest components file
    components_file = find_latest_components_file()
    if not components_file:
        print("No Chillblast component data found. Please run chillblast_scraper.py first.")
        return
    
    print(f"Using components file: {components_file}")
    
    # Load component data
    with open(components_file, 'r') as f:
        components_data = json.load(f)
    
    # Import components
    results = import_components(components_data)
    
    # Print summary
    print("\nImport completed:")
    for category, stats in results.items():
        print(f"  {category.capitalize()}: {stats['existing']} existing + {stats['new']} new = {stats['total']} total")

if __name__ == "__main__":
    main()
