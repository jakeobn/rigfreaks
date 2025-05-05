import json
from app import app
from utils import load_component_data, calculate_total_price
from models import db, PreBuiltConfig

# Define prebuilt configurations
PREBUILT_CONFIGS = [
    {
        "name": "Ryzen 5 5500 RTX 4060 Gaming PC",
        "description": "A powerful mid-range gaming PC featuring the AMD Ryzen 5 5500 CPU and NVIDIA RTX 4060 GPU. Ideal for 1080p gaming with ray tracing and DLSS capabilities.",
        "category": "gaming",
        "components": {
            "cpu": "cpu10",  # Using Ryzen 5 as a placeholder since we don't have the exact 5500 model
            "motherboard": "mobo8",  # A520 chipset motherboard 
            "ram": "ram4",  # 16GB DDR4 3200MT/s memory
            "gpu": "gpu6",  # Using RTX model as placeholder
            "storage": "storage1",  # 2TB NVMe SSD
            "power_supply": "psu2",  # 750W power supply
            "case": "case5",  # Corsair case
            "cooling": "cooling1"  # 240mm AIO liquid cooler
        },
        "special_features": [
            "240mm AIO Liquid Cooling",
            "RTX Ray Tracing & DLSS",
            "Full RGB Lighting",
            "PCIe 4.0 Support",
            "High-Speed 2TB NVMe Storage"
        ],
        "price": 999.99
    },
    {
        "name": "Budget Gaming PC",
        "description": "A cost-effective gaming build capable of running modern games at 1080p with medium settings.",
        "category": "gaming",
        "components": {
            "cpu": "cpu3",  # Intel Core i5-13600K
            "motherboard": "mobo3",  # ASUS TUF Gaming B760M-PLUS WIFI
            "ram": "ram4",  # Crucial Ballistix DDR4 16GB
            "gpu": "gpu4",  # AMD Radeon RX 6700 XT
            "storage": "storage3",  # WD Black SN850X 1TB NVMe SSD
            "power_supply": "psu3",  # be quiet! Pure Power 11 600W
            "case": "case3",  # Corsair 4000D Airflow
        }
    },
    {
        "name": "High-End Gaming PC",
        "description": "A powerful gaming PC designed for 1440p/4K gaming with high framerates and ray tracing capabilities.",
        "category": "gaming",
        "components": {
            "cpu": "cpu5",  # Intel Core i7-13700K
            "motherboard": "mobo1",  # ASUS ROG Maximus Z790 Hero
            "ram": "ram1",  # Corsair Vengeance DDR5 32GB
            "gpu": "gpu3",  # NVIDIA GeForce RTX 4070 Ti
            "storage": "storage1",  # Samsung 990 PRO 2TB NVMe SSD
            "power_supply": "psu2",  # EVGA SuperNOVA 750 G5
            "case": "case1",  # Lian Li O11 Dynamic EVO
        }
    },
    {
        "name": "Ultimate Gaming Rig",
        "description": "The ultimate gaming experience with no compromises. Built for 4K gaming, streaming, and content creation.",
        "category": "gaming",
        "components": {
            "cpu": "cpu1",  # Intel Core i9-13900K
            "motherboard": "mobo1",  # ASUS ROG Maximus Z790 Hero
            "ram": "ram1",  # Corsair Vengeance DDR5 32GB
            "gpu": "gpu1",  # NVIDIA GeForce RTX 4090
            "storage": "storage1",  # Samsung 990 PRO 2TB NVMe SSD
            "power_supply": "psu4",  # Seasonic PRIME TX-1600
            "case": "case1",  # Lian Li O11 Dynamic EVO
        }
    },
    {
        "name": "Budget Productivity PC",
        "description": "An affordable PC for everyday tasks, office work, and light multitasking.",
        "category": "productivity",
        "components": {
            "cpu": "cpu3",  # Intel Core i5-13600K
            "motherboard": "mobo3",  # ASUS TUF Gaming B760M-PLUS WIFI
            "ram": "ram4",  # Crucial Ballistix DDR4 16GB
            "storage": "storage2",  # Crucial MX500 1TB SATA SSD
            "power_supply": "psu3",  # be quiet! Pure Power 11 600W
            "case": "case3",  # Corsair 4000D Airflow
        }
    },
    {
        "name": "Content Creator Workstation",
        "description": "Optimized for video editing, 3D rendering, and other creative workloads.",
        "category": "workstation",
        "components": {
            "cpu": "cpu2",  # AMD Ryzen 9 7950X
            "motherboard": "mobo4",  # GIGABYTE X670E AORUS MASTER
            "ram": "ram1",  # Corsair Vengeance DDR5 32GB
            "gpu": "gpu2",  # AMD Radeon RX 7900 XTX
            "storage": "storage1",  # Samsung 990 PRO 2TB NVMe SSD
            "power_supply": "psu1",  # Corsair RM1000x
            "case": "case2",  # Fractal Design Meshify 2 Compact
        }
    },
    {
        "name": "Compact Gaming PC",
        "description": "A space-saving but powerful gaming PC in a compact form factor.",
        "category": "gaming",
        "components": {
            "cpu": "cpu4",  # AMD Ryzen 7 7700X
            "motherboard": "mobo2",  # MSI MAG B650 TOMAHAWK WIFI
            "ram": "ram3",  # Kingston FURY Beast DDR5 16GB
            "gpu": "gpu3",  # NVIDIA GeForce RTX 4070 Ti
            "storage": "storage3",  # WD Black SN850X 1TB NVMe SSD
            "power_supply": "psu3",  # be quiet! Pure Power 11 600W
            "case": "case4",  # NZXT H7 Flow
        }
    }
]

def create_prebuilt_configs():
    """Create predefined PC configurations in the database"""
    
    # Get components data to calculate prices
    components_data = load_component_data()
    
    # Clear existing prebuilt configs
    PreBuiltConfig.query.delete()
    
    for config_data in PREBUILT_CONFIGS:
        # Create config object
        config = PreBuiltConfig(
            name=config_data["name"],
            description=config_data["description"],
            category=config_data["category"]
        )
        
        # Add component IDs
        for category, component_id in config_data["components"].items():
            setattr(config, f"{category}_id", component_id)
        
        # Set price if provided directly, otherwise calculate from components
        if "price" in config_data:
            config.price = config_data["price"]
        else:
            config_dict = config_data["components"]
            config.price = calculate_total_price(config_dict)
            
        # Set special features if provided
        if "special_features" in config_data:
            config.special_features = json.dumps(config_data["special_features"])
        
        # Add to database
        db.session.add(config)
    
    # Commit changes
    db.session.commit()
    print(f"Created {len(PREBUILT_CONFIGS)} pre-built PC configurations")

# Run this script with Flask app context
if __name__ == "__main__":
    with app.app_context():
        create_prebuilt_configs()