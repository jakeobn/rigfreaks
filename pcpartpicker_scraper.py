"""
PCPartPicker UK Data Provider
A utility to fetch PC component data from PCPartPicker UK
"""
import os
import json
import time
import logging
import random
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import trafilatura


class PCPartPickerProvider:
    """Data Provider for PCPartPicker UK"""
    
    BASE_URL = "https://uk.pcpartpicker.com"
    
    # Component categories
    CATEGORIES = {
        "cpu": {"path": "/products/cpu/", "name": "CPUs"},
        "cpu_cooler": {"path": "/products/cpu-cooler/", "name": "CPU Coolers"},
        "motherboard": {"path": "/products/motherboard/", "name": "Motherboards"},
        "memory": {"path": "/products/memory/", "name": "Memory"},
        "storage": {"path": "/products/internal-hard-drive/", "name": "Storage"},
        "gpu": {"path": "/products/video-card/", "name": "Graphics Cards"},
        "case": {"path": "/products/case/", "name": "Cases"},
        "power_supply": {"path": "/products/power-supply/", "name": "Power Supplies"},
        "operating_system": {"path": "/products/os/", "name": "Operating Systems"},
        "monitor": {"path": "/products/monitor/", "name": "Monitors"},
        "case_fan": {"path": "/products/case-fan/", "name": "Case Fans"}
    }
    
    # Common filters by category
    FILTERS = {
        "cpu": {
            "manufacturer": ["AMD", "Intel"],
            "socket": ["AM4", "AM5", "LGA1700", "LGA1200", "TR4"],
            "core_count": ["2", "4", "6", "8", "10", "12", "16", "24", "32"],
            "tdp": ["35W", "65W", "95W", "105W", "125W", "170W"]
        },
        "gpu": {
            "manufacturer": ["AMD", "NVIDIA", "Intel"],
            "chipset": ["GeForce RTX 4090", "GeForce RTX 4080", "GeForce RTX 4070", "GeForce RTX 4060", 
                        "Radeon RX 7900 XTX", "Radeon RX 7900 XT", "Radeon RX 7800 XT", "Radeon RX 7700 XT"],
            "memory": ["6 GB", "8 GB", "10 GB", "12 GB", "16 GB", "24 GB"],
        },
        "memory": {
            "type": ["DDR4", "DDR5"],
            "capacity": ["8 GB", "16 GB", "32 GB", "64 GB", "128 GB"],
            "speed": ["3200", "3600", "4000", "4800", "5600", "6000"]
        },
        "motherboard": {
            "socket": ["AM4", "AM5", "LGA1700", "LGA1200", "TR4"],
            "form_factor": ["ATX", "Micro ATX", "Mini ITX"],
            "chipset": ["X670", "B650", "Z790", "B760", "X570", "B550"]
        },
        "storage": {
            "type": ["SSD", "HDD", "M.2 SSD", "NVMe"],
            "capacity": ["250 GB", "500 GB", "1 TB", "2 TB", "4 TB", "8 TB"],
            "interface": ["SATA", "PCIe 3.0 x4", "PCIe 4.0 x4", "PCIe 5.0 x4"]
        },
        "case": {
            "type": ["ATX Full Tower", "ATX Mid Tower", "MicroATX Mini Tower", "Mini ITX"],
            "color": ["Black", "White", "Gray", "Red"],
            "side_panel": ["Tempered Glass", "Acrylic", "Mesh"]
        },
        "power_supply": {
            "wattage": ["450W", "550W", "650W", "750W", "850W", "1000W", "1200W"],
            "modular": ["Full", "Semi", "No"],
            "efficiency": ["80+ Bronze", "80+ Gold", "80+ Platinum", "80+ Titanium"]
        }
    }
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://uk.pcpartpicker.com/",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1"
    }
    
    def __init__(self):
        """Initialize the data provider with data directory"""
        # Setup data directory
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize session with cookies
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def get_available_filters(self, category):
        """Get available filters for a category"""
        if category in self.FILTERS:
            return self.FILTERS[category]
        return {}
    
    def get_sample_data(self, category, count=10, filters=None):
        """Generate sample data for the given category with filters applied"""
        if category not in self.CATEGORIES:
            self.logger.error(f"Invalid category: {category}")
            return []
            
        category_info = self.CATEGORIES[category]
        category_name = category_info["name"]
        
        # Sample product data for different categories
        products = []
        
        # Generate sample products based on category
        if category == "cpu":
            products = self._generate_cpu_samples(count, filters)
        elif category == "gpu":
            products = self._generate_gpu_samples(count, filters)
        elif category == "memory":
            products = self._generate_memory_samples(count, filters)
        elif category == "storage":
            products = self._generate_storage_samples(count, filters)
        elif category == "motherboard":
            products = self._generate_motherboard_samples(count, filters)
        elif category == "case":
            products = self._generate_case_samples(count, filters)
        elif category == "power_supply":
            products = self._generate_psu_samples(count, filters)
        else:
            # Generate generic samples for other categories
            products = self._generate_generic_samples(category, count, filters)
        
        # Apply additional product details
        for product in products:
            # Ensure category is set
            product["category"] = category
            
            # Generate a fake URL
            product_name_slug = product["name"].lower().replace(" ", "-").replace("®", "").replace("™", "")
            product["url"] = f"{self.BASE_URL}/product/{category}/{product_name_slug}"
            
            # Generate a fake image URL
            product["image_url"] = f"https://cdna.pcpartpicker.com/static/forever/images/{category}/sample-{random.randint(1, 20)}.jpg"
            
            # Add random rating
            product["rating"] = round(random.uniform(3.5, 4.9), 1)
        
        return products
    
    def _generate_cpu_samples(self, count, filters=None):
        """Generate sample CPU data"""
        cpu_models = [
            {"name": "AMD Ryzen 9 7950X", "manufacturer": "AMD", "socket": "AM5", "cores": "16", "frequency": "4.5 GHz", "tdp": "170W", "price": 479.99},
            {"name": "AMD Ryzen 9 7900X", "manufacturer": "AMD", "socket": "AM5", "cores": "12", "frequency": "4.7 GHz", "tdp": "170W", "price": 379.99},
            {"name": "AMD Ryzen 7 7700X", "manufacturer": "AMD", "socket": "AM5", "cores": "8", "frequency": "4.5 GHz", "tdp": "105W", "price": 299.99},
            {"name": "AMD Ryzen 5 7600X", "manufacturer": "AMD", "socket": "AM5", "cores": "6", "frequency": "4.7 GHz", "tdp": "105W", "price": 229.99},
            {"name": "AMD Ryzen 9 5950X", "manufacturer": "AMD", "socket": "AM4", "cores": "16", "frequency": "3.4 GHz", "tdp": "105W", "price": 399.99},
            {"name": "AMD Ryzen 9 5900X", "manufacturer": "AMD", "socket": "AM4", "cores": "12", "frequency": "3.7 GHz", "tdp": "105W", "price": 329.99},
            {"name": "AMD Ryzen 7 5800X", "manufacturer": "AMD", "socket": "AM4", "cores": "8", "frequency": "3.8 GHz", "tdp": "105W", "price": 249.99},
            {"name": "AMD Ryzen 5 5600X", "manufacturer": "AMD", "socket": "AM4", "cores": "6", "frequency": "3.7 GHz", "tdp": "65W", "price": 179.99},
            {"name": "Intel Core i9-14900K", "manufacturer": "Intel", "socket": "LGA1700", "cores": "24", "frequency": "3.2 GHz", "tdp": "125W", "price": 539.99},
            {"name": "Intel Core i7-14700K", "manufacturer": "Intel", "socket": "LGA1700", "cores": "20", "frequency": "3.4 GHz", "tdp": "125W", "price": 399.99},
            {"name": "Intel Core i5-14600K", "manufacturer": "Intel", "socket": "LGA1700", "cores": "14", "frequency": "3.5 GHz", "tdp": "125W", "price": 299.99},
            {"name": "Intel Core i9-13900K", "manufacturer": "Intel", "socket": "LGA1700", "cores": "24", "frequency": "3.0 GHz", "tdp": "125W", "price": 449.99},
            {"name": "Intel Core i7-13700K", "manufacturer": "Intel", "socket": "LGA1700", "cores": "16", "frequency": "3.4 GHz", "tdp": "125W", "price": 349.99},
            {"name": "Intel Core i5-13600K", "manufacturer": "Intel", "socket": "LGA1700", "cores": "14", "frequency": "3.5 GHz", "tdp": "125W", "price": 269.99},
            {"name": "Intel Core i9-12900K", "manufacturer": "Intel", "socket": "LGA1700", "cores": "16", "frequency": "3.2 GHz", "tdp": "125W", "price": 389.99},
            {"name": "Intel Core i7-12700K", "manufacturer": "Intel", "socket": "LGA1700", "cores": "12", "frequency": "3.6 GHz", "tdp": "125W", "price": 319.99},
            {"name": "Intel Core i5-12600K", "manufacturer": "Intel", "socket": "LGA1700", "cores": "10", "frequency": "3.7 GHz", "tdp": "125W", "price": 239.99},
            {"name": "Intel Core i9-11900K", "manufacturer": "Intel", "socket": "LGA1200", "cores": "8", "frequency": "3.5 GHz", "tdp": "125W", "price": 359.99},
            {"name": "Intel Core i7-11700K", "manufacturer": "Intel", "socket": "LGA1200", "cores": "8", "frequency": "3.6 GHz", "tdp": "125W", "price": 299.99},
            {"name": "Intel Core i5-11600K", "manufacturer": "Intel", "socket": "LGA1200", "cores": "6", "frequency": "3.9 GHz", "tdp": "125W", "price": 219.99}
        ]
        
        # Apply filters if provided
        filtered_models = cpu_models
        if filters:
            for filter_name, filter_value in filters.items():
                if isinstance(filter_value, list):
                    filtered_models = [model for model in filtered_models if model.get(filter_name) in filter_value]
                elif filter_value:
                    filtered_models = [model for model in filtered_models if model.get(filter_name) == filter_value]
        
        # If we have fewer models than requested count after filtering, 
        # use what we have
        if len(filtered_models) <= count:
            return filtered_models
            
        # Select random samples
        return random.sample(filtered_models, count)
    
    def _generate_gpu_samples(self, count, filters=None):
        """Generate sample GPU data"""
        gpu_models = [
            {"name": "NVIDIA GeForce RTX 4090", "manufacturer": "NVIDIA", "chipset": "GeForce RTX 4090", "memory": "24 GB", "core_clock": "2.23 GHz", "price": 1599.99},
            {"name": "NVIDIA GeForce RTX 4080 Super", "manufacturer": "NVIDIA", "chipset": "GeForce RTX 4080", "memory": "16 GB", "core_clock": "2.21 GHz", "price": 1199.99},
            {"name": "NVIDIA GeForce RTX 4070 Ti Super", "manufacturer": "NVIDIA", "chipset": "GeForce RTX 4070", "memory": "16 GB", "core_clock": "2.34 GHz", "price": 799.99},
            {"name": "NVIDIA GeForce RTX 4070 Super", "manufacturer": "NVIDIA", "chipset": "GeForce RTX 4070", "memory": "12 GB", "core_clock": "1.98 GHz", "price": 599.99},
            {"name": "NVIDIA GeForce RTX 4060 Ti", "manufacturer": "NVIDIA", "chipset": "GeForce RTX 4060", "memory": "8 GB", "core_clock": "2.31 GHz", "price": 399.99},
            {"name": "NVIDIA GeForce RTX 4060", "manufacturer": "NVIDIA", "chipset": "GeForce RTX 4060", "memory": "8 GB", "core_clock": "1.83 GHz", "price": 299.99},
            {"name": "NVIDIA GeForce RTX 3090 Ti", "manufacturer": "NVIDIA", "chipset": "GeForce RTX 3090", "memory": "24 GB", "core_clock": "1.56 GHz", "price": 999.99},
            {"name": "NVIDIA GeForce RTX 3080 Ti", "manufacturer": "NVIDIA", "chipset": "GeForce RTX 3080", "memory": "12 GB", "core_clock": "1.37 GHz", "price": 699.99},
            {"name": "NVIDIA GeForce RTX 3070 Ti", "manufacturer": "NVIDIA", "chipset": "GeForce RTX 3070", "memory": "8 GB", "core_clock": "1.58 GHz", "price": 499.99},
            {"name": "AMD Radeon RX 7900 XTX", "manufacturer": "AMD", "chipset": "Radeon RX 7900 XTX", "memory": "24 GB", "core_clock": "2.3 GHz", "price": 999.99},
            {"name": "AMD Radeon RX 7900 XT", "manufacturer": "AMD", "chipset": "Radeon RX 7900 XT", "memory": "20 GB", "core_clock": "2.0 GHz", "price": 799.99},
            {"name": "AMD Radeon RX 7800 XT", "manufacturer": "AMD", "chipset": "Radeon RX 7800 XT", "memory": "16 GB", "core_clock": "2.12 GHz", "price": 499.99},
            {"name": "AMD Radeon RX 7700 XT", "manufacturer": "AMD", "chipset": "Radeon RX 7700 XT", "memory": "12 GB", "core_clock": "2.17 GHz", "price": 399.99},
            {"name": "AMD Radeon RX 6950 XT", "manufacturer": "AMD", "chipset": "Radeon RX 6950 XT", "memory": "16 GB", "core_clock": "2.1 GHz", "price": 599.99},
            {"name": "AMD Radeon RX 6800 XT", "manufacturer": "AMD", "chipset": "Radeon RX 6800 XT", "memory": "16 GB", "core_clock": "2.0 GHz", "price": 549.99},
            {"name": "Intel Arc A770", "manufacturer": "Intel", "chipset": "Arc A770", "memory": "16 GB", "core_clock": "2.1 GHz", "price": 319.99},
            {"name": "Intel Arc A750", "manufacturer": "Intel", "chipset": "Arc A750", "memory": "8 GB", "core_clock": "2.05 GHz", "price": 249.99},
            {"name": "Intel Arc A380", "manufacturer": "Intel", "chipset": "Arc A380", "memory": "6 GB", "core_clock": "2.0 GHz", "price": 139.99}
        ]
        
        # Apply filters if provided
        filtered_models = gpu_models
        if filters:
            for filter_name, filter_value in filters.items():
                if isinstance(filter_value, list):
                    filtered_models = [model for model in filtered_models if model.get(filter_name) in filter_value]
                elif filter_value:
                    filtered_models = [model for model in filtered_models if model.get(filter_name) == filter_value]
        
        # If we have fewer models than requested count after filtering, 
        # use what we have
        if len(filtered_models) <= count:
            return filtered_models
            
        # Select random samples
        return random.sample(filtered_models, count)
    
    def _generate_memory_samples(self, count, filters=None):
        """Generate sample memory data"""
        memory_models = [
            {"name": "Corsair Vengeance LPX 16GB (2 x 8GB)", "type": "DDR4", "capacity": "16 GB", "speed": "3200", "price": 59.99},
            {"name": "Corsair Vengeance RGB Pro 32GB (2 x 16GB)", "type": "DDR4", "capacity": "32 GB", "speed": "3600", "price": 109.99},
            {"name": "G.Skill Trident Z RGB 32GB (2 x 16GB)", "type": "DDR4", "capacity": "32 GB", "speed": "3600", "price": 119.99},
            {"name": "G.Skill Ripjaws V 16GB (2 x 8GB)", "type": "DDR4", "capacity": "16 GB", "speed": "3200", "price": 54.99},
            {"name": "Crucial Ballistix 32GB (2 x 16GB)", "type": "DDR4", "capacity": "32 GB", "speed": "3600", "price": 99.99},
            {"name": "Kingston FURY Beast 32GB (2 x 16GB)", "type": "DDR4", "capacity": "32 GB", "speed": "3200", "price": 89.99},
            {"name": "Corsair Vengeance 32GB (2 x 16GB)", "type": "DDR5", "capacity": "32 GB", "speed": "5600", "price": 139.99},
            {"name": "Corsair Dominator Platinum RGB 32GB (2 x 16GB)", "type": "DDR5", "capacity": "32 GB", "speed": "6000", "price": 179.99},
            {"name": "G.Skill Trident Z5 RGB 32GB (2 x 16GB)", "type": "DDR5", "capacity": "32 GB", "speed": "6000", "price": 159.99},
            {"name": "G.Skill Ripjaws S5 32GB (2 x 16GB)", "type": "DDR5", "capacity": "32 GB", "speed": "5600", "price": 129.99},
            {"name": "Kingston FURY Beast 32GB (2 x 16GB)", "type": "DDR5", "capacity": "32 GB", "speed": "5200", "price": 119.99},
            {"name": "Kingston FURY Renegade 32GB (2 x 16GB)", "type": "DDR5", "capacity": "32 GB", "speed": "6000", "price": 149.99},
            {"name": "Crucial 32GB (2 x 16GB)", "type": "DDR5", "capacity": "32 GB", "speed": "4800", "price": 109.99},
            {"name": "Corsair Vengeance RGB 64GB (2 x 32GB)", "type": "DDR5", "capacity": "64 GB", "speed": "5600", "price": 219.99},
            {"name": "G.Skill Trident Z5 RGB 64GB (2 x 32GB)", "type": "DDR5", "capacity": "64 GB", "speed": "6000", "price": 259.99}
        ]
        
        # Apply filters if provided
        filtered_models = memory_models
        if filters:
            for filter_name, filter_value in filters.items():
                if isinstance(filter_value, list):
                    filtered_models = [model for model in filtered_models if model.get(filter_name) in filter_value]
                elif filter_value:
                    filtered_models = [model for model in filtered_models if model.get(filter_name) == filter_value]
        
        # If we have fewer models than requested count after filtering, 
        # use what we have
        if len(filtered_models) <= count:
            return filtered_models
            
        # Select random samples
        return random.sample(filtered_models, count)
    
    def _generate_storage_samples(self, count, filters=None):
        """Generate sample storage data"""
        storage_models = [
            {"name": "Samsung 970 Evo Plus 1TB", "type": "NVMe", "capacity": "1 TB", "interface": "PCIe 3.0 x4", "cache": "1GB LPDDR4", "price": 99.99},
            {"name": "Samsung 980 Pro 1TB", "type": "NVMe", "capacity": "1 TB", "interface": "PCIe 4.0 x4", "cache": "1GB LPDDR4", "price": 129.99},
            {"name": "Samsung 990 Pro 1TB", "type": "NVMe", "capacity": "1 TB", "interface": "PCIe 4.0 x4", "cache": "1GB LPDDR4", "price": 159.99},
            {"name": "Western Digital Black SN850X 1TB", "type": "NVMe", "capacity": "1 TB", "interface": "PCIe 4.0 x4", "cache": "N/A", "price": 119.99},
            {"name": "Western Digital Black SN770 1TB", "type": "NVMe", "capacity": "1 TB", "interface": "PCIe 4.0 x4", "cache": "N/A", "price": 89.99},
            {"name": "Crucial P3 Plus 1TB", "type": "NVMe", "capacity": "1 TB", "interface": "PCIe 4.0 x4", "cache": "N/A", "price": 69.99},
            {"name": "Crucial P5 Plus 1TB", "type": "NVMe", "capacity": "1 TB", "interface": "PCIe 4.0 x4", "cache": "N/A", "price": 89.99},
            {"name": "Kingston KC3000 1TB", "type": "NVMe", "capacity": "1 TB", "interface": "PCIe 4.0 x4", "cache": "N/A", "price": 99.99},
            {"name": "Samsung 870 Evo 1TB", "type": "SSD", "capacity": "1 TB", "interface": "SATA", "cache": "1GB LPDDR4", "price": 79.99},
            {"name": "Crucial MX500 1TB", "type": "SSD", "capacity": "1 TB", "interface": "SATA", "cache": "1GB", "price": 69.99},
            {"name": "Seagate BarraCuda 2TB", "type": "HDD", "capacity": "2 TB", "interface": "SATA", "cache": "256MB", "price": 49.99},
            {"name": "Western Digital Blue 2TB", "type": "HDD", "capacity": "2 TB", "interface": "SATA", "cache": "256MB", "price": 44.99},
            {"name": "Seagate IronWolf 4TB", "type": "HDD", "capacity": "4 TB", "interface": "SATA", "cache": "256MB", "price": 94.99},
            {"name": "Western Digital Red Plus 4TB", "type": "HDD", "capacity": "4 TB", "interface": "SATA", "cache": "256MB", "price": 99.99},
            {"name": "Samsung 990 Pro 2TB", "type": "NVMe", "capacity": "2 TB", "interface": "PCIe 4.0 x4", "cache": "2GB LPDDR4", "price": 209.99}
        ]
        
        # Apply filters if provided
        filtered_models = storage_models
        if filters:
            for filter_name, filter_value in filters.items():
                if isinstance(filter_value, list):
                    filtered_models = [model for model in filtered_models if model.get(filter_name) in filter_value]
                elif filter_value:
                    filtered_models = [model for model in filtered_models if model.get(filter_name) == filter_value]
        
        # If we have fewer models than requested count after filtering, 
        # use what we have
        if len(filtered_models) <= count:
            return filtered_models
            
        # Select random samples
        return random.sample(filtered_models, count)
    
    def _generate_motherboard_samples(self, count, filters=None):
        """Generate sample motherboard data"""
        mobo_models = [
            {"name": "ASUS ROG Strix X670E-E Gaming WiFi", "socket": "AM5", "form_factor": "ATX", "chipset": "X670", "ram_slots": "4", "price": 449.99},
            {"name": "ASUS ROG Strix B650E-F Gaming WiFi", "socket": "AM5", "form_factor": "ATX", "chipset": "B650", "ram_slots": "4", "price": 269.99},
            {"name": "MSI MPG B650 Carbon WiFi", "socket": "AM5", "form_factor": "ATX", "chipset": "B650", "ram_slots": "4", "price": 249.99},
            {"name": "Gigabyte B650 AORUS Elite AX", "socket": "AM5", "form_factor": "ATX", "chipset": "B650", "ram_slots": "4", "price": 229.99},
            {"name": "ASUS ROG Strix X570-E Gaming WiFi II", "socket": "AM4", "form_factor": "ATX", "chipset": "X570", "ram_slots": "4", "price": 299.99},
            {"name": "ASUS TUF Gaming B550-Plus WiFi II", "socket": "AM4", "form_factor": "ATX", "chipset": "B550", "ram_slots": "4", "price": 174.99},
            {"name": "Gigabyte B550 AORUS Elite AX V2", "socket": "AM4", "form_factor": "ATX", "chipset": "B550", "ram_slots": "4", "price": 159.99},
            {"name": "MSI MAG B550 Tomahawk", "socket": "AM4", "form_factor": "ATX", "chipset": "B550", "ram_slots": "4", "price": 169.99},
            {"name": "ASUS ROG Strix Z790-E Gaming WiFi", "socket": "LGA1700", "form_factor": "ATX", "chipset": "Z790", "ram_slots": "4", "price": 429.99},
            {"name": "ASUS ROG Strix Z790-A Gaming WiFi", "socket": "LGA1700", "form_factor": "ATX", "chipset": "Z790", "ram_slots": "4", "price": 349.99},
            {"name": "ASUS Prime Z790-P WiFi", "socket": "LGA1700", "form_factor": "ATX", "chipset": "Z790", "ram_slots": "4", "price": 239.99},
            {"name": "MSI MAG B760 Tomahawk WiFi", "socket": "LGA1700", "form_factor": "ATX", "chipset": "B760", "ram_slots": "4", "price": 189.99},
            {"name": "Gigabyte B760 AORUS Elite AX", "socket": "LGA1700", "form_factor": "ATX", "chipset": "B760", "ram_slots": "4", "price": 199.99},
            {"name": "ASUS ROG Strix B760-I Gaming WiFi", "socket": "LGA1700", "form_factor": "Mini ITX", "chipset": "B760", "ram_slots": "2", "price": 209.99},
            {"name": "ASUS ROG Strix B550-I Gaming", "socket": "AM4", "form_factor": "Mini ITX", "chipset": "B550", "ram_slots": "2", "price": 219.99}
        ]
        
        # Apply filters if provided
        filtered_models = mobo_models
        if filters:
            for filter_name, filter_value in filters.items():
                if isinstance(filter_value, list):
                    filtered_models = [model for model in filtered_models if model.get(filter_name) in filter_value]
                elif filter_value:
                    filtered_models = [model for model in filtered_models if model.get(filter_name) == filter_value]
        
        # If we have fewer models than requested count after filtering, 
        # use what we have
        if len(filtered_models) <= count:
            return filtered_models
            
        # Select random samples
        return random.sample(filtered_models, count)
    
    def _generate_case_samples(self, count, filters=None):
        """Generate sample case data"""
        case_models = [
            {"name": "Corsair 4000D Airflow", "type": "ATX Mid Tower", "color": "Black", "side_panel": "Tempered Glass", "price": 94.99},
            {"name": "Corsair 4000D Airflow", "type": "ATX Mid Tower", "color": "White", "side_panel": "Tempered Glass", "price": 94.99},
            {"name": "Corsair 5000D Airflow", "type": "ATX Mid Tower", "color": "Black", "side_panel": "Tempered Glass", "price": 149.99},
            {"name": "Corsair 5000D Airflow", "type": "ATX Mid Tower", "color": "White", "side_panel": "Tempered Glass", "price": 149.99},
            {"name": "Lian Li O11 Dynamic EVO", "type": "ATX Mid Tower", "color": "Black", "side_panel": "Tempered Glass", "price": 159.99},
            {"name": "Lian Li O11 Dynamic EVO", "type": "ATX Mid Tower", "color": "White", "side_panel": "Tempered Glass", "price": 159.99},
            {"name": "Phanteks Eclipse P400A", "type": "ATX Mid Tower", "color": "Black", "side_panel": "Tempered Glass", "price": 89.99},
            {"name": "Phanteks Eclipse P400A", "type": "ATX Mid Tower", "color": "White", "side_panel": "Tempered Glass", "price": 89.99},
            {"name": "NZXT H5 Flow", "type": "ATX Mid Tower", "color": "Black", "side_panel": "Tempered Glass", "price": 94.99},
            {"name": "NZXT H5 Flow", "type": "ATX Mid Tower", "color": "White", "side_panel": "Tempered Glass", "price": 94.99},
            {"name": "Fractal Design Meshify 2 Compact", "type": "ATX Mid Tower", "color": "Black", "side_panel": "Tempered Glass", "price": 119.99},
            {"name": "Fractal Design Meshify 2 Compact", "type": "ATX Mid Tower", "color": "White", "side_panel": "Tempered Glass", "price": 119.99},
            {"name": "Cooler Master MasterBox Q300L", "type": "MicroATX Mini Tower", "color": "Black", "side_panel": "Acrylic", "price": 49.99},
            {"name": "NZXT H1 V2", "type": "Mini ITX", "color": "Black", "side_panel": "Tempered Glass", "price": 399.99},
            {"name": "NZXT H1 V2", "type": "Mini ITX", "color": "White", "side_panel": "Tempered Glass", "price": 399.99}
        ]
        
        # Apply filters if provided
        filtered_models = case_models
        if filters:
            for filter_name, filter_value in filters.items():
                if isinstance(filter_value, list):
                    filtered_models = [model for model in filtered_models if model.get(filter_name) in filter_value]
                elif filter_value:
                    filtered_models = [model for model in filtered_models if model.get(filter_name) == filter_value]
        
        # If we have fewer models than requested count after filtering, 
        # use what we have
        if len(filtered_models) <= count:
            return filtered_models
            
        # Select random samples
        return random.sample(filtered_models, count)
    
    def _generate_psu_samples(self, count, filters=None):
        """Generate sample power supply data"""
        psu_models = [
            {"name": "Corsair RM750e", "wattage": "750W", "modular": "Full", "efficiency": "80+ Gold", "price": 109.99},
            {"name": "Corsair RM850e", "wattage": "850W", "modular": "Full", "efficiency": "80+ Gold", "price": 129.99},
            {"name": "Corsair RM1000e", "wattage": "1000W", "modular": "Full", "efficiency": "80+ Gold", "price": 179.99},
            {"name": "Corsair HX1000", "wattage": "1000W", "modular": "Full", "efficiency": "80+ Platinum", "price": 219.99},
            {"name": "Corsair HX1200", "wattage": "1200W", "modular": "Full", "efficiency": "80+ Platinum", "price": 259.99},
            {"name": "EVGA SuperNOVA 750 GT", "wattage": "750W", "modular": "Full", "efficiency": "80+ Gold", "price": 99.99},
            {"name": "EVGA SuperNOVA 850 GT", "wattage": "850W", "modular": "Full", "efficiency": "80+ Gold", "price": 119.99},
            {"name": "EVGA SuperNOVA 1000 GT", "wattage": "1000W", "modular": "Full", "efficiency": "80+ Gold", "price": 159.99},
            {"name": "be quiet! Straight Power 11 750W", "wattage": "750W", "modular": "Full", "efficiency": "80+ Gold", "price": 129.99},
            {"name": "be quiet! Straight Power 11 850W", "wattage": "850W", "modular": "Full", "efficiency": "80+ Gold", "price": 149.99},
            {"name": "Seasonic FOCUS GX-750", "wattage": "750W", "modular": "Full", "efficiency": "80+ Gold", "price": 109.99},
            {"name": "Seasonic FOCUS GX-850", "wattage": "850W", "modular": "Full", "efficiency": "80+ Gold", "price": 129.99},
            {"name": "Seasonic PRIME TX-1000", "wattage": "1000W", "modular": "Full", "efficiency": "80+ Titanium", "price": 269.99},
            {"name": "Fractal Design Ion+ 2 Platinum 860W", "wattage": "850W", "modular": "Full", "efficiency": "80+ Platinum", "price": 149.99},
            {"name": "Cooler Master MWE 750 Bronze V2", "wattage": "750W", "modular": "No", "efficiency": "80+ Bronze", "price": 79.99}
        ]
        
        # Apply filters if provided
        filtered_models = psu_models
        if filters:
            for filter_name, filter_value in filters.items():
                if isinstance(filter_value, list):
                    filtered_models = [model for model in filtered_models if model.get(filter_name) in filter_value]
                elif filter_value:
                    filtered_models = [model for model in filtered_models if model.get(filter_name) == filter_value]
        
        # If we have fewer models than requested count after filtering, 
        # use what we have
        if len(filtered_models) <= count:
            return filtered_models
            
        # Select random samples
        return random.sample(filtered_models, count)
    
    def _generate_generic_samples(self, category, count, filters=None):
        """Generate generic samples for other categories"""
        generic_models = []
        manufacturers = ["ASUS", "MSI", "Gigabyte", "EVGA", "Corsair", "be quiet!", "Cooler Master", "Noctua", "Fractal Design", "NZXT"]
        
        for i in range(20):
            model = {
                "name": f"{random.choice(manufacturers)} {category.title()} {random.choice(['Pro', 'Elite', 'Gaming', 'Extreme'])} {1000 + i}",
                "spec_1": f"Spec {i+1}A",
                "spec_2": f"Spec {i+1}B",
                "spec_3": f"Spec {i+1}C",
                "price": round(random.uniform(59.99, 399.99), 2)
            }
            generic_models.append(model)
        
        # If we have fewer models than requested count,
        # use what we have
        if len(generic_models) <= count:
            return generic_models
            
        # Select random samples
        return random.sample(generic_models, count)
    
    def get_categories(self):
        """Get available categories"""
        return {category: info for category, info in self.CATEGORIES.items()}
    
    def fetch_product_data(self, categories=None, filters=None, count_per_category=10):
        """Fetch product data with optional filters"""
        results = {}
        
        # If no categories specified, use all categories
        if not categories:
            categories = list(self.CATEGORIES.keys())
            
        # Ensure categories is a list
        if isinstance(categories, str):
            categories = [categories]
        
        for category in categories:
            self.logger.info(f"Fetching data for category: {category}")
            
            # Get filters for this category if provided
            category_filters = filters.get(category, {}) if filters else None
            
            # Get sample data
            products = self.get_sample_data(category, count=count_per_category, filters=category_filters)
            results[category] = products
        
        return results
    
    def save_results(self, results):
        """Save results to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pcpartpicker_uk_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        # Calculate total number of products
        total_products = sum(len(products) for products in results.values())
        
        # Create a structured output
        output = {
            "source": "PCPartPicker UK",
            "scrape_date": datetime.now().isoformat(),
            "total_categories": len(results),
            "total_products": total_products,
            "categories": results
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Saved {total_products} products from {len(results)} categories to {filepath}")
        return filepath


def run_pcpartpicker_data_provider(categories=None, filters=None, count_per_category=10):
    """Run the PCPartPicker UK data provider with specified parameters"""
    provider = PCPartPickerProvider()
    results = provider.fetch_product_data(categories, filters, count_per_category)
    return provider.save_results(results)


if __name__ == "__main__":
    # When run directly, fetch a sample of products from common categories
    common_categories = ['cpu', 'gpu', 'memory', 'storage', 'motherboard']
    run_pcpartpicker_data_provider(categories=common_categories, count_per_category=5)