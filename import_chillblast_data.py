"""Import Chillblast data into the application database

This script imports product data scraped from Chillblast into our application's database.
It creates PreBuiltConfig entries with appropriate component mappings.
"""

import os
import json
import sys
from datetime import datetime
from app import app, db
from models import PreBuiltConfig
from chillblast_scraper import scrape_all_products, scrape_layout_patterns, extract_design_assets

# Data directory
DATA_DIR = "scraped_data"

def map_component_to_local_id(component_type, component_name):
    """Map component names from Chillblast to our local component IDs.
    
    This function attempts to find the best match for external component names
    in our local component database.
    """
    # CPU mapping
    if component_type == "cpu":
        if "Ryzen 9" in component_name:
            return "ryzen9_7950x"
        elif "Ryzen 7" in component_name:
            return "ryzen7_7700x"
        elif "Ryzen 5" in component_name:
            return "ryzen5_7600x"
        elif "Core i9" in component_name:
            return "corei9_13900k"
        elif "Core i7" in component_name:
            return "corei7_13700k"
        elif "Core i5" in component_name:
            return "corei5_13600k"
    
    # GPU mapping
    elif component_type == "gpu":
        if "RTX 4090" in component_name:
            return "rtx4090"
        elif "RTX 4080" in component_name:
            return "rtx4080"
        elif "RTX 4070" in component_name:
            return "rtx4070"
        elif "RTX 4060" in component_name:
            return "rtx4060"
        elif "RX 7900" in component_name:
            return "rx7900xtx"
        elif "RX 7800" in component_name:
            return "rx7800xt"
    
    # Motherboard mapping
    elif component_type == "motherboard":
        if "X670" in component_name:
            return "asus_x670e"
        elif "B650" in component_name:
            return "msi_b650"
        elif "Z790" in component_name:
            return "asus_z790"
        elif "B760" in component_name:
            return "msi_b760"
    
    # RAM mapping
    elif component_type == "ram":
        if "64GB" in component_name:
            return "corsair_64gb_ddr5"
        elif "32GB" in component_name:
            return "corsair_32gb_ddr5"
        elif "16GB" in component_name:
            return "corsair_16gb_ddr5"
    
    # Storage mapping
    elif component_type == "storage":
        if "4TB" in component_name:
            return "samsung_4tb_nvme"
        elif "2TB" in component_name:
            return "samsung_2tb_nvme"
        elif "1TB" in component_name:
            return "samsung_1tb_nvme"
    
    # Power supply mapping
    elif component_type == "power_supply":
        if "1000W" in component_name or "1200W" in component_name:
            return "corsair_1000w"
        elif "850W" in component_name:
            return "corsair_850w"
        elif "750W" in component_name:
            return "corsair_750w"
        else:
            return "corsair_650w"
    
    # Case mapping
    elif component_type == "case":
        if "Fractal" in component_name:
            return "fractal_meshify"
        elif "NZXT" in component_name:
            return "nzxt_h7"
        else:
            return "corsair_5000d"
    
    # Cooling mapping
    elif component_type == "cooling":
        if "Liquid" in component_name or "AIO" in component_name:
            return "corsair_h150i"
        else:
            return "noctua_nh_d15"
    
    # Default fallback mappings
    defaults = {
        "cpu": "ryzen7_7700x",
        "gpu": "rtx4070",
        "motherboard": "asus_x670e",
        "ram": "corsair_32gb_ddr5",
        "storage": "samsung_1tb_nvme",
        "power_supply": "corsair_850w",
        "case": "corsair_5000d",
        "cooling": "corsair_h150i"
    }
    
    return defaults.get(component_type)

def extract_component_from_specs(specs, key_patterns):
    """Extract component info from specifications using key pattern matching."""
    for spec_key, spec_value in specs.items():
        for pattern in key_patterns:
            if pattern.lower() in spec_key.lower():
                return spec_value
    return None

def parse_product_to_config(product):
    """Parse a Chillblast product into our PreBuiltConfig format."""
    specs = product.get('specifications', {})
    
    # Extract components based on specification patterns
    cpu_name = extract_component_from_specs(specs, ["Processor", "CPU"])
    gpu_name = extract_component_from_specs(specs, ["Graphics", "GPU"])
    motherboard_name = extract_component_from_specs(specs, ["Motherboard"])
    ram_name = extract_component_from_specs(specs, ["Memory", "RAM"])
    storage_name = extract_component_from_specs(specs, ["Storage", "SSD", "Hard Drive"])
    psu_name = extract_component_from_specs(specs, ["Power Supply", "PSU"])
    case_name = extract_component_from_specs(specs, ["Case"])
    cooling_name = extract_component_from_specs(specs, ["Cooling", "CPU Cooler"])
    
    # Map to our component IDs
    cpu_id = map_component_to_local_id("cpu", cpu_name) if cpu_name else None
    gpu_id = map_component_to_local_id("gpu", gpu_name) if gpu_name else None
    motherboard_id = map_component_to_local_id("motherboard", motherboard_name) if motherboard_name else None
    ram_id = map_component_to_local_id("ram", ram_name) if ram_name else None
    storage_id = map_component_to_local_id("storage", storage_name) if storage_name else None
    power_supply_id = map_component_to_local_id("power_supply", psu_name) if psu_name else None
    case_id = map_component_to_local_id("case", case_name) if case_name else None
    cooling_id = map_component_to_local_id("cooling", cooling_name) if cooling_name else None
    
    # Determine category
    category = product.get('category', 'gaming')
    
    # Create PreBuiltConfig object
    config = {
        'name': product.get('name', 'Unknown PC'),
        'description': product.get('description', ''),
        'category': category,
        'price': product.get('price', 0.0),
        'special_features': json.dumps([
            "Industry-leading 5 year warranty",
            "Free next-day delivery",
            "Built by expert technicians"
        ]),
        'cpu_id': cpu_id,
        'motherboard_id': motherboard_id,
        'ram_id': ram_id,
        'gpu_id': gpu_id,
        'storage_id': storage_id,
        'power_supply_id': power_supply_id,
        'case_id': case_id,
        'cooling_id': cooling_id
    }
    
    return config

def import_products(products):
    """Import products into the database."""
    with app.app_context():
        # Clear existing prebuilt configs if requested
        if len(sys.argv) > 1 and sys.argv[1] == '--clear':
            print("Clearing existing prebuilt configurations...")
            db.session.query(PreBuiltConfig).delete()
            db.session.commit()
        
        imported_count = 0
        for product in products:
            config_data = parse_product_to_config(product)
            
            # Check if this product already exists (by name)
            existing = PreBuiltConfig.query.filter_by(name=config_data['name']).first()
            if existing:
                print(f"Product already exists: {config_data['name']}")
                continue
            
            # Create new PreBuiltConfig
            config = PreBuiltConfig(**config_data)
            db.session.add(config)
            imported_count += 1
        
        db.session.commit()
        print(f"Imported {imported_count} new products")

def import_from_file(filename):
    """Import products from a previously scraped JSON file."""
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []
    
    with open(file_path, 'r') as f:
        products = json.load(f)
    
    print(f"Loaded {len(products)} products from {filename}")
    return products

def find_latest_data_file(prefix):
    """Find the latest data file with the given prefix."""
    if not os.path.exists(DATA_DIR):
        return None
    
    files = [f for f in os.listdir(DATA_DIR) if f.startswith(prefix) and f.endswith('.json')]
    if not files:
        return None
    
    # Sort files by timestamp (assuming format: prefix_YYYYMMDD_HHMMSS.json)
    files.sort(reverse=True)
    return files[0]

def main():
    """Main function to run the importer."""
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Determine whether to scrape or use existing data
    if len(sys.argv) > 1 and sys.argv[1] == '--scrape':
        print("Scraping new data from Chillblast website...")
        scrape_layout_patterns()
        extract_design_assets()
        all_products, detailed_products = scrape_all_products()
        products_to_import = detailed_products
    else:
        # Find the latest detailed products file
        latest_file = find_latest_data_file("chillblast_products_")
        if latest_file:
            print(f"Using existing data file: {latest_file}")
            products_to_import = import_from_file(latest_file)
        else:
            print("No existing data file found. Use --scrape to fetch new data.")
            return
    
    # Import products into database
    import_products(products_to_import)

if __name__ == "__main__":
    main()
