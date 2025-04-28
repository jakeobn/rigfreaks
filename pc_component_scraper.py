"""
PC Component Scraper
A standalone scraper for PC components that works with international websites
"""
import os
import sys
import json
import time
import logging
import requests
import threading
from datetime import datetime
from bs4 import BeautifulSoup
from dataclasses import dataclass

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Component categories for PC parts
COMPONENT_CATEGORIES = {
    "cpu": "CPU",
    "gpu": "Graphics Card",
    "motherboard": "Motherboard",
    "memory": "RAM",
    "storage": "Storage",
    "case": "Case",
    "power_supply": "Power Supply",
    "cpu_cooler": "CPU Cooler"
}

# Headers for making requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}


@dataclass
class Component:
    """A PC component with its details"""
    name: str
    price: str
    category: str
    url: str
    image_url: str
    source: str
    specs: dict = None


class PCComponentScraper:
    """Scraper for PC components from various online sources"""
    
    def __init__(self):
        """Initialize the scraper"""
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Sites to scrape
        self.sites = {
            "newegg": {
                "base_url": "https://www.newegg.com/p/pl?d={search_term}",
                "scraper": self._scrape_newegg
            },
            "pcpartpicker": {
                "base_url": "https://pcpartpicker.com/search/?q={search_term}",
                "scraper": self._scrape_pcpartpicker
            }
        }
    
    def fetch_components(self, category, search_term=None, max_items=10):
        """
        Fetch components for a specific category
        
        Args:
            category (str): Component category (cpu, gpu, etc.)
            search_term (str): Optional search term to use instead of category
            max_items (int): Maximum number of components to return
            
        Returns:
            list: List of Component objects
        """
        if search_term is None:
            search_term = category
            
            # Use more specific search terms for better results
            if category == "cpu":
                search_term = "processor cpu"
            elif category == "gpu":
                search_term = "graphics card gpu"
            elif category == "memory":
                search_term = "ram memory ddr4 ddr5"
            elif category == "storage":
                search_term = "ssd hdd storage"
            elif category == "power_supply":
                search_term = "power supply psu"
                
        logger.info(f"Searching for {search_term} in category {category}")
        
        # List to store all components
        all_components = []
        
        # Fetch from each site
        threads = []
        thread_results = {}
        
        for site_name, site_info in self.sites.items():
            thread = threading.Thread(
                target=self._fetch_from_site,
                args=(site_name, site_info, search_term, category, thread_results)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Combine results
        for components in thread_results.values():
            all_components.extend(components)
            
        # Sort by price (lowest first)
        all_components.sort(key=lambda x: self._parse_price(x.price))
        
        # Limit the number of components
        if max_items and len(all_components) > max_items:
            all_components = all_components[:max_items]
            
        logger.info(f"Found {len(all_components)} components for category {category}")
        return all_components
    
    def _fetch_from_site(self, site_name, site_info, search_term, category, results):
        """Fetch components from a specific site"""
        try:
            url = site_info["base_url"].format(search_term=search_term.replace(" ", "+"))
            logger.info(f"Fetching from {site_name}: {url}")
            
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                components = site_info["scraper"](soup, category)
                logger.info(f"Found {len(components)} components from {site_name}")
                results[site_name] = components
            else:
                logger.warning(f"Failed to fetch from {site_name}: Status code {response.status_code}")
                results[site_name] = []
        except Exception as e:
            logger.error(f"Error fetching from {site_name}: {str(e)}")
            results[site_name] = []
    
    def _scrape_newegg(self, soup, category):
        """Scrape components from Newegg"""
        components = []
        
        # Find all product items
        items = soup.select(".item-cell")
        
        for item in items:
            try:
                # Extract product details
                name_elem = item.select_one(".item-title")
                price_elem = item.select_one(".price-current")
                
                if not name_elem or not price_elem:
                    continue
                
                name = name_elem.text.strip()
                price = price_elem.text.strip()
                
                # Get URL and image
                url = name_elem["href"] if name_elem.has_attr("href") else ""
                image_elem = item.select_one(".item-img img")
                image_url = image_elem["src"] if image_elem and image_elem.has_attr("src") else ""
                
                # Extract basic specs from name
                specs = self._extract_specs(name, category)
                
                # Create component object
                component = Component(
                    name=name,
                    price=price,
                    category=category,
                    url=url,
                    image_url=image_url,
                    source="Newegg",
                    specs=specs
                )
                
                components.append(component)
            except Exception as e:
                logger.error(f"Error scraping Newegg item: {str(e)}")
                continue
                
        return components
    
    def _scrape_pcpartpicker(self, soup, category):
        """Scrape components from PCPartPicker"""
        components = []
        
        # Find all product items
        items = soup.select(".list-unstyled li.search-result")
        
        for item in items:
            try:
                # Extract product details
                name_elem = item.select_one(".search-result__heading")
                price_elem = item.select_one(".search-result__price")
                
                if not name_elem or not price_elem:
                    continue
                
                name = name_elem.text.strip()
                price = price_elem.text.strip()
                
                # Get URL and image
                url_elem = item.select_one("a.search-result__link")
                url = "https://pcpartpicker.com" + url_elem["href"] if url_elem and url_elem.has_attr("href") else ""
                
                image_elem = item.select_one(".search-result__image img")
                image_url = image_elem["src"] if image_elem and image_elem.has_attr("src") else ""
                
                # Extract basic specs from name
                specs = self._extract_specs(name, category)
                
                # Create component object
                component = Component(
                    name=name,
                    price=price,
                    category=category,
                    url=url,
                    image_url=image_url,
                    source="PCPartPicker",
                    specs=specs
                )
                
                components.append(component)
            except Exception as e:
                logger.error(f"Error scraping PCPartPicker item: {str(e)}")
                continue
                
        return components
    
    def _parse_price(self, price_str):
        """Parse a price string to a float value"""
        try:
            # Remove currency symbols and commas
            price = price_str.replace("$", "").replace("£", "").replace("€", "").replace(",", "")
            
            # Find the first number in the string
            import re
            match = re.search(r'\d+(\.\d+)?', price)
            if match:
                return float(match.group(0))
            return 0.0
        except:
            return 0.0
    
    def _extract_specs(self, title, category):
        """Extract basic specifications from a product title"""
        specs = {}
        title_lower = title.lower()
        
        # CPU
        if category == "cpu":
            # Check for Intel or AMD
            if "intel" in title_lower:
                specs["manufacturer"] = "Intel"
                # Check for Intel CPU series
                if "i9" in title_lower:
                    specs["series"] = "Core i9"
                elif "i7" in title_lower:
                    specs["series"] = "Core i7"
                elif "i5" in title_lower:
                    specs["series"] = "Core i5"
                elif "i3" in title_lower:
                    specs["series"] = "Core i3"
                    
                # Check for Intel generation
                for gen in range(8, 15):  # 8th to 14th gen
                    if f"{gen}" in title_lower or f"{gen}th" in title_lower:
                        specs["generation"] = str(gen)
                        break
                        
            elif "amd" in title_lower or "ryzen" in title_lower:
                specs["manufacturer"] = "AMD"
                # Check for Ryzen series
                if "ryzen 9" in title_lower:
                    specs["series"] = "Ryzen 9"
                elif "ryzen 7" in title_lower:
                    specs["series"] = "Ryzen 7"
                elif "ryzen 5" in title_lower:
                    specs["series"] = "Ryzen 5"
                elif "ryzen 3" in title_lower:
                    specs["series"] = "Ryzen 3"
                    
                # Check for AMD generation
                for gen in [3, 5, 7, 9]:  # Ryzen 3000, 5000, 7000, 9000
                    if f"{gen}000" in title_lower:
                        specs["generation"] = str(gen) + "000"
                        break
            
            # Check for cores
            import re
            core_match = re.search(r'(\d+)[ -]core', title_lower)
            if core_match:
                specs["cores"] = core_match.group(1)
                
        # GPU
        elif category == "gpu":
            # Check for manufacturer
            if "nvidia" in title_lower or "rtx" in title_lower or "gtx" in title_lower:
                specs["manufacturer"] = "NVIDIA"
                
                # Check for RTX/GTX series
                if "rtx" in title_lower:
                    specs["series"] = "RTX"
                    # Look for RTX model numbers
                    for model in ["4090", "4080", "4070", "4060", "3090", "3080", "3070", "3060"]:
                        if model in title_lower:
                            specs["model"] = model
                            break
                elif "gtx" in title_lower:
                    specs["series"] = "GTX"
                    # Look for GTX model numbers
                    for model in ["1660", "1650", "1080", "1070", "1060", "1050"]:
                        if model in title_lower:
                            specs["model"] = model
                            break
                            
            elif "amd" in title_lower or "radeon" in title_lower:
                specs["manufacturer"] = "AMD"
                
                # Check for Radeon series
                if "rx" in title_lower:
                    specs["series"] = "RX"
                    # Look for RX model numbers
                    for model in ["7900", "7800", "7700", "7600", "6900", "6800", "6700", "6600"]:
                        if model in title_lower:
                            specs["model"] = model
                            break
            
            # Check for VRAM
            import re
            vram_match = re.search(r'(\d+)gb', title_lower.replace(" ", ""))
            if vram_match:
                specs["memory"] = f"{vram_match.group(1)} GB"
                
        # RAM
        elif category == "memory":
            # Check for DDR generation
            if "ddr5" in title_lower:
                specs["type"] = "DDR5"
            elif "ddr4" in title_lower:
                specs["type"] = "DDR4"
                
            # Check for capacity
            import re
            capacity_match = re.search(r'(\d+)gb', title_lower.replace(" ", ""))
            if capacity_match:
                specs["capacity"] = f"{capacity_match.group(1)} GB"
                
            # Check for speed
            speed_match = re.search(r'(\d+)mhz', title_lower.replace(" ", ""))
            if speed_match:
                specs["speed"] = f"{speed_match.group(1)} MHz"
                
        # Storage
        elif category == "storage":
            # Check for SSD vs HDD
            if "ssd" in title_lower:
                specs["type"] = "SSD"
                if "nvme" in title_lower:
                    specs["interface"] = "NVMe"
                elif "sata" in title_lower:
                    specs["interface"] = "SATA"
            elif "hdd" in title_lower:
                specs["type"] = "HDD"
                
            # Check for capacity
            import re
            tb_match = re.search(r'(\d+)tb', title_lower.replace(" ", ""))
            if tb_match:
                specs["capacity"] = f"{tb_match.group(1)} TB"
            else:
                gb_match = re.search(r'(\d+)gb', title_lower.replace(" ", ""))
                if gb_match:
                    specs["capacity"] = f"{gb_match.group(1)} GB"
                    
        # Motherboard
        elif category == "motherboard":
            # Check for manufacturer
            for brand in ["asus", "msi", "gigabyte", "asrock"]:
                if brand in title_lower:
                    specs["manufacturer"] = brand.upper()
                    break
                    
            # Check for chipset
            for chipset in ["z790", "z690", "z590", "b760", "b660", "b560", "x670", "x570", "b650", "b550"]:
                if chipset in title_lower:
                    specs["chipset"] = chipset.upper()
                    break
                    
            # Check for form factor
            if "atx" in title_lower:
                if "micro" in title_lower or "matx" in title_lower:
                    specs["form_factor"] = "Micro ATX"
                elif "mini" in title_lower or "itx" in title_lower:
                    specs["form_factor"] = "Mini ITX"
                else:
                    specs["form_factor"] = "ATX"
                    
            # Check for socket
            if "am5" in title_lower:
                specs["socket"] = "AM5"
            elif "am4" in title_lower:
                specs["socket"] = "AM4"
            elif "lga1700" in title_lower or "lga 1700" in title_lower:
                specs["socket"] = "LGA1700"
            elif "lga1200" in title_lower or "lga 1200" in title_lower:
                specs["socket"] = "LGA1200"
                
        # Power Supply
        elif category == "power_supply":
            # Check for wattage
            import re
            watt_match = re.search(r'(\d+)w', title_lower.replace(" ", ""))
            if watt_match:
                specs["wattage"] = f"{watt_match.group(1)}W"
                
            # Check for 80+ certification
            for cert in ["80+ titanium", "80+ platinum", "80+ gold", "80+ silver", "80+ bronze"]:
                if cert in title_lower or cert.replace("+ ", "+") in title_lower:
                    specs["certification"] = cert.upper()
                    break
                    
            # Check if modular
            if "modular" in title_lower:
                if "semi" in title_lower:
                    specs["modular"] = "Semi"
                elif "fully" in title_lower or "full" in title_lower:
                    specs["modular"] = "Full"
                else:
                    specs["modular"] = "Yes"
                    
        return specs
    
    def fetch_all_categories(self, count_per_category=5):
        """Fetch components for all categories"""
        results = {}
        
        # Use threading for parallel fetching
        threads = []
        
        for category in COMPONENT_CATEGORIES:
            thread = threading.Thread(
                target=self._fetch_category_thread,
                args=(category, count_per_category, results)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        return results
    
    def _fetch_category_thread(self, category, count_limit, results_dict):
        """Thread function to fetch components for a category"""
        try:
            components = self.fetch_components(category, max_items=count_limit)
            results_dict[category] = components
            logger.info(f"Fetched {len(components)} components for category {category}")
        except Exception as e:
            logger.error(f"Error in fetch thread for {category}: {str(e)}")
            results_dict[category] = []
    
    def save_results(self, results):
        """Save scraped results to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pc_components_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        # Convert components to dictionaries
        output = {
            "source": "PC Component Scraper",
            "scrape_date": datetime.now().isoformat(),
            "total_categories": len(results),
            "total_components": sum(len(components) for components in results.values()),
            "categories": {}
        }
        
        for category, components in results.items():
            output["categories"][category] = [
                {
                    "name": c.name,
                    "price": c.price,
                    "category": c.category,
                    "url": c.url,
                    "image_url": c.image_url,
                    "source": c.source,
                    "specs": c.specs
                }
                for c in components
            ]
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved {output['total_components']} components from {len(results)} categories to {filepath}")
        return filepath


def run_component_scraper(categories=None, count_per_category=5):
    """Run the PC component scraper"""
    scraper = PCComponentScraper()
    
    if categories:
        results = {}
        for category in categories:
            components = scraper.fetch_components(category, max_items=count_per_category)
            results[category] = components
    else:
        results = scraper.fetch_all_categories(count_per_category=count_per_category)
        
    return scraper.save_results(results)


if __name__ == "__main__":
    # When run directly, fetch components from common categories
    common_categories = ['cpu', 'gpu', 'memory', 'storage', 'motherboard']
    run_component_scraper(categories=common_categories, count_per_category=3)