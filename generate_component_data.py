"""Generate component data for PC builder using available component images.

This script creates JSON files with component data for each category,
using the images we've organized from attached_assets.
"""

import os
import json
import glob

# Directory where our component images are stored
IMAGES_DIR = os.path.join("static", "images", "components")

# Directory where our component data will be stored
DATA_DIR = "data"

# Component data templates
COMPONENT_TEMPLATES = {
    "cpu": [
        {
            "name": "AMD Ryzen 9 9900X3D",
            "brand": "AMD",
            "price": 649.99,
            "description": "AMD's flagship gaming CPU with 3D V-Cache technology, offering unmatched gaming performance with 16 cores and 32 threads.",
            "specs": {
                "Cores": "16",
                "Threads": "32",
                "Base Clock": "4.3 GHz",
                "Boost Clock": "5.5 GHz",
                "Cache": "144MB (16+128)",
                "TDP": "120W"
            },
            "socket": "AM5"
        },
        {
            "name": "Intel Core i9-14900K",
            "brand": "Intel",
            "price": 599.99,
            "description": "Intel's high-end desktop processor featuring a hybrid architecture with 24 cores (8P+16E) and 32 threads for extreme performance.",
            "specs": {
                "Cores": "24 (8P+16E)",
                "Threads": "32",
                "Base Clock": "3.2 GHz",
                "Boost Clock": "6.0 GHz",
                "Cache": "36MB",
                "TDP": "125W"
            },
            "socket": "LGA 1700"
        },
        {
            "name": "AMD Ryzen 7 7800X3D",
            "brand": "AMD",
            "price": 449.99,
            "description": "The ultimate gaming processor with AMD's 3D V-Cache technology, 8 cores and 16 threads for exceptional gaming performance.",
            "specs": {
                "Cores": "8",
                "Threads": "16",
                "Base Clock": "4.2 GHz",
                "Boost Clock": "5.0 GHz",
                "Cache": "104MB (8+96)",
                "TDP": "120W"
            },
            "socket": "AM5"
        }
    ],
    "motherboard": [
        {
            "name": "ASUS ROG Strix Z790-E Gaming WiFi",
            "brand": "ASUS",
            "price": 449.99,
            "description": "Premium Z790 motherboard with Wi-Fi 6E, PCIe 5.0, and extensive cooling options for enthusiast builds.",
            "specs": {
                "Chipset": "Intel Z790",
                "Memory": "4x DIMM, Max. 128GB, DDR5",
                "Expansion Slots": "2x PCIe 5.0 x16, 1x PCIe 4.0 x16",
                "Storage": "4x M.2, 6x SATA",
                "Networking": "Wi-Fi 6E, 2.5Gb Ethernet"
            },
            "socket": "LGA 1700",
            "form_factor": "ATX",
            "chipset": "Z790"
        },
        {
            "name": "ASUS TUF Gaming B650-Plus WiFi",
            "brand": "ASUS",
            "price": 239.99,
            "description": "Durable B650 motherboard with military-grade components, Wi-Fi 6, and PCIe 5.0 support for reliable AMD builds.",
            "specs": {
                "Chipset": "AMD B650",
                "Memory": "4x DIMM, Max. 128GB, DDR5",
                "Expansion Slots": "1x PCIe 5.0 x16, 2x PCIe 4.0 x16",
                "Storage": "3x M.2, 4x SATA",
                "Networking": "Wi-Fi 6, 2.5Gb Ethernet"
            },
            "socket": "AM5",
            "form_factor": "ATX",
            "chipset": "B650"
        },
        {
            "name": "Gigabyte X870 AORUS Elite WiFi7",
            "brand": "Gigabyte",
            "price": 329.99,
            "description": "High-performance X870 motherboard with WiFi 7, PCIe 5.0, and robust power delivery for advanced AMD systems.",
            "specs": {
                "Chipset": "AMD X870",
                "Memory": "4x DIMM, Max. 192GB, DDR5",
                "Expansion Slots": "2x PCIe 5.0 x16, 1x PCIe 4.0 x4",
                "Storage": "4x M.2, 6x SATA",
                "Networking": "Wi-Fi 7, 2.5Gb Ethernet"
            },
            "socket": "AM5",
            "form_factor": "ATX",
            "chipset": "X870"
        }
    ],
    "ram": [
        {
            "name": "Kingston FURY Beast RGB 32GB DDR5-6000",
            "brand": "Kingston",
            "price": 199.99,
            "description": "High-performance DDR5 memory with RGB lighting, designed for gamers and enthusiasts seeking both style and speed.",
            "specs": {
                "Capacity": "32GB (2x16GB)",
                "Speed": "6000MHz",
                "Latency": "CL36",
                "Voltage": "1.35V",
                "RGB": "Yes"
            },
            "capacity": "32GB",
            "speed": "6000MHz",
            "type": "DDR5"
        },
        {
            "name": "Corsair Vengeance RGB Pro 32GB DDR4-3600",
            "brand": "Corsair",
            "price": 129.99,
            "description": "Optimized for Intel and AMD DDR4 platforms with RGB lighting for a customizable look.",
            "specs": {
                "Capacity": "32GB (2x16GB)",
                "Speed": "3600MHz",
                "Latency": "CL18",
                "Voltage": "1.35V",
                "RGB": "Yes"
            },
            "capacity": "32GB",
            "speed": "3600MHz",
            "type": "DDR4"
        },
        {
            "name": "Corsair Vengeance 32GB DDR5-5600",
            "brand": "Corsair",
            "price": 169.99,
            "description": "High-performance DDR5 memory designed for the latest platforms, offering excellent stability and overclocking potential.",
            "specs": {
                "Capacity": "32GB (2x16GB)",
                "Speed": "5600MHz",
                "Latency": "CL36",
                "Voltage": "1.25V",
                "RGB": "No"
            },
            "capacity": "32GB",
            "speed": "5600MHz",
            "type": "DDR5"
        }
    ],
    "gpu": [
        {
            "name": "NVIDIA GeForce RTX 4090 24GB",
            "brand": "NVIDIA",
            "price": 1599.99,
            "description": "NVIDIA's flagship graphics card delivering unprecedented performance for gaming and content creation with 24GB of GDDR6X memory.",
            "specs": {
                "CUDA Cores": "16384",
                "Memory": "24GB GDDR6X",
                "Memory Bus": "384-bit",
                "Boost Clock": "2.52 GHz",
                "TDP": "450W"
            },
            "vram": "24GB",
            "core_clock": "2.52 GHz"
        },
        {
            "name": "ASUS TUF Gaming GeForce RTX 4080 Super 16GB",
            "brand": "ASUS",
            "price": 1199.99,
            "description": "Built for reliable high-performance gaming with enhanced cooling and military-grade components.",
            "specs": {
                "CUDA Cores": "10240",
                "Memory": "16GB GDDR6X",
                "Memory Bus": "256-bit",
                "Boost Clock": "2.55 GHz",
                "TDP": "320W"
            },
            "vram": "16GB",
            "core_clock": "2.55 GHz"
        },
        {
            "name": "ASUS TUF Gaming Radeon RX 7900 XTX 24GB",
            "brand": "ASUS",
            "price": 999.99,
            "description": "AMD's top-tier graphics card with advanced cooling, 24GB of memory, and exceptional gaming performance.",
            "specs": {
                "Stream Processors": "12288",
                "Memory": "24GB GDDR6",
                "Memory Bus": "384-bit",
                "Boost Clock": "2.5 GHz",
                "TDP": "355W"
            },
            "vram": "24GB",
            "core_clock": "2.5 GHz"
        }
    ],
    "storage": [
        {
            "name": "Samsung 990 PRO 1TB NVMe SSD",
            "brand": "Samsung",
            "price": 149.99,
            "description": "Samsung's flagship PCIe 4.0 NVMe SSD delivering exceptional speeds and reliability for gamers and professionals.",
            "specs": {
                "Capacity": "1TB",
                "Interface": "PCIe 4.0 x4 NVMe",
                "Sequential Read": "7450 MB/s",
                "Sequential Write": "6900 MB/s",
                "Endurance": "600 TBW"
            },
            "capacity": "1TB",
            "type": "NVMe SSD",
            "interface": "PCIe 4.0"
        },
        {
            "name": "Corsair MP600 PRO XT 2TB NVMe SSD",
            "brand": "Corsair",
            "price": 239.99,
            "description": "High-performance Gen4 NVMe SSD with a custom heatsink design for sustained performance under heavy workloads.",
            "specs": {
                "Capacity": "2TB",
                "Interface": "PCIe 4.0 x4 NVMe",
                "Sequential Read": "7100 MB/s",
                "Sequential Write": "6800 MB/s",
                "Endurance": "1200 TBW"
            },
            "capacity": "2TB",
            "type": "NVMe SSD",
            "interface": "PCIe 4.0"
        },
        {
            "name": "Samsung 870 EVO 1TB SATA SSD",
            "brand": "Samsung",
            "price": 89.99,
            "description": "Reliable and fast SATA SSD perfect for everyday computing and storage expansion needs.",
            "specs": {
                "Capacity": "1TB",
                "Interface": "SATA 6Gb/s",
                "Sequential Read": "560 MB/s",
                "Sequential Write": "530 MB/s",
                "Endurance": "600 TBW"
            },
            "capacity": "1TB",
            "type": "SATA SSD",
            "interface": "SATA 6Gb/s"
        }
    ],
    "power_supply": [
        {
            "name": "Corsair RM850e 850W 80+ Gold",
            "brand": "Corsair",
            "price": 129.99,
            "description": "Fully modular power supply with 80 PLUS Gold efficiency and quiet operation for high-performance systems.",
            "specs": {
                "Wattage": "850W",
                "Efficiency": "80+ Gold",
                "Modular": "Fully Modular",
                "Fan": "135mm FDB",
                "Warranty": "10 Years"
            },
            "wattage": "850W",
            "efficiency": "80+ Gold",
            "modular": True
        },
        {
            "name": "Corsair RM1000x 1000W 80+ Gold",
            "brand": "Corsair",
            "price": 189.99,
            "description": "Premium fully modular power supply with high-quality components for enthusiast builds and multi-GPU setups.",
            "specs": {
                "Wattage": "1000W",
                "Efficiency": "80+ Gold",
                "Modular": "Fully Modular",
                "Fan": "135mm FDB",
                "Warranty": "10 Years"
            },
            "wattage": "1000W",
            "efficiency": "80+ Gold",
            "modular": True
        },
        {
            "name": "Corsair RM1200x 1200W 80+ Gold",
            "brand": "Corsair",
            "price": 229.99,
            "description": "High-capacity fully modular power supply designed for extreme performance systems and workstations.",
            "specs": {
                "Wattage": "1200W",
                "Efficiency": "80+ Gold",
                "Modular": "Fully Modular",
                "Fan": "140mm FDB",
                "Warranty": "10 Years"
            },
            "wattage": "1200W",
            "efficiency": "80+ Gold",
            "modular": True
        }
    ],
    "case": [
        {
            "name": "Fractal Design North White TG",
            "brand": "Fractal Design",
            "price": 139.99,
            "description": "Elegant ATX case with wood-accented front panel, tempered glass side panel, and excellent airflow design.",
            "specs": {
                "Form Factor": "Mid Tower",
                "Motherboard Support": "E-ATX, ATX, Micro-ATX, Mini-ITX",
                "Front I/O": "2x USB 3.0, 1x USB-C, Audio",
                "Included Fans": "2x 140mm",
                "Radiator Support": "Up to 360mm"
            },
            "form_factor": "Mid Tower",
            "color": "White"
        },
        {
            "name": "Corsair 5000D RGB Airflow",
            "brand": "Corsair",
            "price": 189.99,
            "description": "High-airflow mid-tower case with RGB lighting, ample cooling options, and easy cable management.",
            "specs": {
                "Form Factor": "Mid Tower",
                "Motherboard Support": "E-ATX, ATX, Micro-ATX, Mini-ITX",
                "Front I/O": "2x USB 3.0, 1x USB-C, Audio",
                "Included Fans": "3x 120mm RGB",
                "Radiator Support": "Up to 360mm"
            },
            "form_factor": "Mid Tower",
            "color": "Black"
        },
        {
            "name": "Lian Li O11 Dynamic EVO White",
            "brand": "Lian Li",
            "price": 169.99,
            "description": "Versatile dual-chamber case with tempered glass panels, exceptional cooling support, and a sophisticated design.",
            "specs": {
                "Form Factor": "Mid Tower",
                "Motherboard Support": "E-ATX, ATX, Micro-ATX, Mini-ITX",
                "Front I/O": "2x USB 3.0, 1x USB-C, Audio",
                "Included Fans": "None",
                "Radiator Support": "Up to 360mm"
            },
            "form_factor": "Mid Tower",
            "color": "White"
        }
    ],
    "cooling": [
        {
            "name": "Corsair iCUE H150i RGB Elite 360mm AIO",
            "brand": "Corsair",
            "price": 189.99,
            "description": "Premium 360mm all-in-one liquid cooler with RGB lighting and excellent thermal performance.",
            "specs": {
                "Type": "Liquid",
                "Radiator Size": "360mm",
                "Fan Speed": "450-2100 RPM",
                "Noise Level": "10-30 dBA",
                "RGB": "Yes"
            },
            "type": "Liquid",
            "size": "360mm"
        },
        {
            "name": "DeepCool AG620 ARGB CPU Air Cooler",
            "brand": "DeepCool",
            "price": 69.99,
            "description": "Dual-tower air cooler with 6 heatpipes and ARGB lighting for efficient and quiet cooling.",
            "specs": {
                "Type": "Air",
                "Fan Speed": "500-1850 RPM",
                "Noise Level": "18-31 dBA",
                "Heatpipes": "6",
                "RGB": "Yes"
            },
            "type": "Air",
            "size": "Dual Tower"
        },
        {
            "name": "Noctua NH-D15 Chromax Black",
            "brand": "Noctua",
            "price": 109.99,
            "description": "Flagship dual-tower air cooler with outstanding performance and virtually silent operation in an all-black design.",
            "specs": {
                "Type": "Air",
                "Fan Speed": "300-1500 RPM",
                "Noise Level": "24.6 dBA",
                "Heatpipes": "6",
                "RGB": "No"
            },
            "type": "Air",
            "size": "Dual Tower"
        }
    ]
}

# Ensure component data directory exists
def ensure_dirs():
    """Create necessary data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    print("Data directory created.")

# Generate component JSON files
def generate_component_data():
    """Generate component data JSON files with images."""
    ensure_dirs()
    
    results = {}
    
    for category, templates in COMPONENT_TEMPLATES.items():
        # Get all component images for this category
        image_dir = os.path.join(IMAGES_DIR, category)
        if not os.path.exists(image_dir):
            print(f"Warning: No image directory found for {category}")
            continue
        
        images = glob.glob(os.path.join(image_dir, "*.*"))
        
        # Map images to components
        components = []
        for i, template in enumerate(templates):
            component = template.copy()
            component["id"] = str(1000 + i)
            
            # Assign image if available
            if i < len(images):
                image_path = images[i]
                # Get relative path from static folder (for web URLs)
                rel_path = os.path.relpath(image_path, "static")
                component["image"] = "/" + rel_path.replace("\\", "/")  # Ensure forward slashes for web URLs
            else:
                component["image"] = "/images/placeholder.png"
            
            components.append(component)
        
        # Save to JSON file
        output_file = os.path.join(DATA_DIR, f"{category}.json")
        with open(output_file, 'w') as f:
            json.dump(components, f, indent=2)
        
        results[category] = len(components)
    
    return results

def main():
    """Main function to run the component data generator."""
    print("Starting component data generation...")
    results = generate_component_data()
    
    print("\nComponent data generation complete!")
    print("Summary:")
    for category, count in results.items():
        print(f"  {category.capitalize()}: {count} components")

if __name__ == "__main__":
    main()
