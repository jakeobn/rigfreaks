"""
Component Data Scraper
Uses the Content-Aggregator repository to fetch PC component data
"""
import os
import sys
import json
import time
import logging
import threading
from datetime import datetime

# Add the Content-Aggregator directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
content_aggregator_path = os.path.join(current_dir, 'Content-Aggregator')
sys.path.append(content_aggregator_path)

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


class ContentScraper:
    """Component data scraper using Content-Aggregator"""
    
    def __init__(self):
        """Initialize the content scraper"""
        # Setup data directory
        self.data_dir = os.path.join(current_dir, 'scraped_data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_component_data(self, component_name, category, count_limit=10):
        """
        Fetch component data using Content-Aggregator
        
        Args:
            component_name (str): The name of the component to search for
            category (str): The category of component (cpu, gpu, etc.)
            count_limit (int): Maximum number of results to return
            
        Returns:
            list: List of components with their details
        """
        logger.info(f"Searching for {component_name} in category {category}")
        
        # Dynamic import to avoid import issues
        import importlib.util
        ca_path = os.path.join(content_aggregator_path, 'content_aggregator.py')
        spec = importlib.util.spec_from_file_location("content_aggregator", ca_path)
        ca = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ca)
        
        # Map our category to Content-Aggregator's "Computer Parts" category
        # All PC components will use the "Computer Parts" category in Content-Aggregator
        part_cat = "Computer Parts"
        
        try:
            # Get the parts from Content-Aggregator
            start_time = time.time()
            part_list = ca.get_part_details(component_name, part_cat)
            logger.info(f"Search completed in {time.time() - start_time:.2f} seconds")
            
            # Limit the number of results
            if count_limit and len(part_list) > count_limit:
                part_list = part_list[:count_limit]
            
            # Convert to our format
            components = []
            for part in part_list:
                component = {
                    "name": part.title,
                    "price": part.price,
                    "category": category,
                    "url": part.link,
                    "image_url": part.img_link,
                    "source": part.site,
                    "specs": self._extract_specs(part.title, category)
                }
                components.append(component)
            
            return components
        
        except Exception as e:
            logger.error(f"Error fetching component data: {str(e)}")
            return []
    
    def fetch_multiple_components(self, categories=None, search_terms=None, count_per_category=5):
        """
        Fetch data for multiple component categories
        
        Args:
            categories (list): List of categories to fetch
            search_terms (dict): Dictionary mapping categories to search terms
            count_per_category (int): Number of components to fetch per category
            
        Returns:
            dict: Dictionary of components by category
        """
        results = {}
        
        # If no categories specified, use all categories
        if not categories:
            categories = list(COMPONENT_CATEGORIES.keys())
            
        # Default search terms if none provided
        if not search_terms:
            search_terms = {
                "cpu": "processor",
                "gpu": "graphics card",
                "motherboard": "motherboard",
                "memory": "ram",
                "storage": "ssd",
                "case": "computer case",
                "power_supply": "power supply",
                "cpu_cooler": "cpu cooler"
            }
        
        # Use threading for parallel fetching
        threads = []
        
        for category in categories:
            if category not in COMPONENT_CATEGORIES:
                logger.warning(f"Skipping invalid category: {category}")
                continue
            
            # Get the search term for this category
            search_term = search_terms.get(category, category)
            
            # Create a thread for this category
            thread = threading.Thread(
                target=self._fetch_category_thread,
                args=(category, search_term, count_per_category, results)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        return results
    
    def _fetch_category_thread(self, category, search_term, count_limit, results_dict):
        """Thread function to fetch components for a category"""
        try:
            components = self.fetch_component_data(search_term, category, count_limit)
            results_dict[category] = components
            logger.info(f"Fetched {len(components)} components for category {category}")
        except Exception as e:
            logger.error(f"Error in fetch thread for {category}: {str(e)}")
            results_dict[category] = []
    
    def _extract_specs(self, title, category):
        """
        Extract specifications from component title
        This is a simple extraction based on the component title
        
        Args:
            title (str): Component title
            category (str): Component category
            
        Returns:
            dict: Component specifications
        """
        specs = {}
        title_lower = title.lower()
        
        # Extract basic specs based on title keywords
        if category == "cpu":
            # Extract cores if mentioned
            if "core" in title_lower:
                cores_index = title_lower.find("core")
                if cores_index > 0 and cores_index < len(title_lower) - 5:
                    pre_text = title_lower[max(0, cores_index - 10):cores_index].strip()
                    if pre_text and pre_text[-1].isdigit():
                        for i in range(len(pre_text) - 1, -1, -1):
                            if not pre_text[i].isdigit():
                                cores = pre_text[i+1:]
                                specs["cores"] = cores
                                break
            
            # Check for common CPU families
            if "ryzen" in title_lower:
                specs["manufacturer"] = "AMD"
                if "3" in title_lower:
                    specs["generation"] = "3"
                elif "5" in title_lower:
                    specs["generation"] = "5"
                elif "7" in title_lower:
                    specs["generation"] = "7"
                elif "9" in title_lower:
                    specs["generation"] = "9"
            
            elif "intel" in title_lower:
                specs["manufacturer"] = "Intel"
                if "i3" in title_lower:
                    specs["series"] = "i3"
                elif "i5" in title_lower:
                    specs["series"] = "i5"
                elif "i7" in title_lower:
                    specs["series"] = "i7"
                elif "i9" in title_lower:
                    specs["series"] = "i9"
        
        elif category == "gpu":
            # Check for common GPU manufacturers
            if "nvidia" in title_lower or "rtx" in title_lower or "gtx" in title_lower:
                specs["manufacturer"] = "NVIDIA"
                
                # Extract RTX/GTX model numbers
                if "rtx" in title_lower:
                    specs["series"] = "RTX"
                    if "3060" in title_lower:
                        specs["model"] = "3060"
                    elif "3070" in title_lower:
                        specs["model"] = "3070"
                    elif "3080" in title_lower:
                        specs["model"] = "3080"
                    elif "3090" in title_lower:
                        specs["model"] = "3090"
                    elif "4060" in title_lower:
                        specs["model"] = "4060"
                    elif "4070" in title_lower:
                        specs["model"] = "4070"
                    elif "4080" in title_lower:
                        specs["model"] = "4080"
                    elif "4090" in title_lower:
                        specs["model"] = "4090"
                elif "gtx" in title_lower:
                    specs["series"] = "GTX"
                    if "1650" in title_lower:
                        specs["model"] = "1650"
                    elif "1660" in title_lower:
                        specs["model"] = "1660"
            
            elif "amd" in title_lower or "radeon" in title_lower:
                specs["manufacturer"] = "AMD"
                
                # Extract Radeon model numbers
                if "rx" in title_lower:
                    specs["series"] = "RX"
                    if "6600" in title_lower:
                        specs["model"] = "6600"
                    elif "6700" in title_lower:
                        specs["model"] = "6700"
                    elif "6800" in title_lower:
                        specs["model"] = "6800"
                    elif "6900" in title_lower:
                        specs["model"] = "6900"
                    elif "7600" in title_lower:
                        specs["model"] = "7600"
                    elif "7700" in title_lower:
                        specs["model"] = "7700"
                    elif "7800" in title_lower:
                        specs["model"] = "7800"
                    elif "7900" in title_lower:
                        specs["model"] = "7900"
            
            # Check for memory capacity
            if "gb" in title_lower:
                gb_index = title_lower.find("gb")
                if gb_index > 0:
                    pre_text = title_lower[max(0, gb_index - 5):gb_index].strip()
                    if pre_text and pre_text[-1].isdigit():
                        for i in range(len(pre_text) - 1, -1, -1):
                            if not pre_text[i].isdigit():
                                memory = pre_text[i+1:]
                                specs["memory"] = f"{memory} GB"
                                break
        
        elif category == "memory":
            # Check for common RAM specs
            if "ddr4" in title_lower:
                specs["type"] = "DDR4"
            elif "ddr5" in title_lower:
                specs["type"] = "DDR5"
            
            # Extract capacity
            if "gb" in title_lower:
                gb_index = title_lower.find("gb")
                if gb_index > 0:
                    pre_text = title_lower[max(0, gb_index - 5):gb_index].strip()
                    if pre_text and pre_text[-1].isdigit():
                        for i in range(len(pre_text) - 1, -1, -1):
                            if not pre_text[i].isdigit():
                                capacity = pre_text[i+1:]
                                specs["capacity"] = f"{capacity} GB"
                                break
            
            # Extract speed
            if "mhz" in title_lower:
                mhz_index = title_lower.find("mhz")
                if mhz_index > 0:
                    pre_text = title_lower[max(0, mhz_index - 5):mhz_index].strip()
                    if pre_text and pre_text[-1].isdigit():
                        for i in range(len(pre_text) - 1, -1, -1):
                            if not pre_text[i].isdigit():
                                speed = pre_text[i+1:]
                                specs["speed"] = f"{speed} MHz"
                                break
        
        elif category == "storage":
            # Extract storage type
            if "ssd" in title_lower:
                specs["type"] = "SSD"
                if "nvme" in title_lower:
                    specs["interface"] = "NVMe"
                elif "m.2" in title_lower:
                    specs["form_factor"] = "M.2"
                elif "sata" in title_lower:
                    specs["interface"] = "SATA"
            elif "hdd" in title_lower:
                specs["type"] = "HDD"
                if "sata" in title_lower:
                    specs["interface"] = "SATA"
            
            # Extract capacity
            if "tb" in title_lower:
                tb_index = title_lower.find("tb")
                if tb_index > 0:
                    pre_text = title_lower[max(0, tb_index - 5):tb_index].strip()
                    if pre_text and pre_text[-1].isdigit():
                        for i in range(len(pre_text) - 1, -1, -1):
                            if not pre_text[i].isdigit() and pre_text[i] != '.':
                                capacity = pre_text[i+1:]
                                specs["capacity"] = f"{capacity} TB"
                                break
            elif "gb" in title_lower:
                gb_index = title_lower.find("gb")
                if gb_index > 0:
                    pre_text = title_lower[max(0, gb_index - 5):gb_index].strip()
                    if pre_text and pre_text[-1].isdigit():
                        for i in range(len(pre_text) - 1, -1, -1):
                            if not pre_text[i].isdigit():
                                capacity = pre_text[i+1:]
                                specs["capacity"] = f"{capacity} GB"
                                break
        
        elif category == "motherboard":
            # Check for common motherboard specs
            if "atx" in title_lower and "mini" not in title_lower and "micro" not in title_lower:
                specs["form_factor"] = "ATX"
            elif "micro" in title_lower and "atx" in title_lower:
                specs["form_factor"] = "Micro ATX"
            elif "mini" in title_lower and "itx" in title_lower:
                specs["form_factor"] = "Mini ITX"
            
            # Check for chipset
            for chipset in ["b550", "b650", "b660", "b760", "x570", "x670", "z590", "z690", "z790"]:
                if chipset in title_lower:
                    specs["chipset"] = chipset.upper()
            
            # Check for manufacturer
            if "asus" in title_lower:
                specs["manufacturer"] = "ASUS"
            elif "gigabyte" in title_lower:
                specs["manufacturer"] = "Gigabyte"
            elif "msi" in title_lower:
                specs["manufacturer"] = "MSI"
            elif "asrock" in title_lower:
                specs["manufacturer"] = "ASRock"
            
            # Check for socket
            if "am4" in title_lower:
                specs["socket"] = "AM4"
            elif "am5" in title_lower:
                specs["socket"] = "AM5"
            elif "lga1700" in title_lower or "lga 1700" in title_lower:
                specs["socket"] = "LGA1700"
            elif "lga1200" in title_lower or "lga 1200" in title_lower:
                specs["socket"] = "LGA1200"
        
        elif category == "power_supply":
            # Extract wattage
            if "w" in title_lower or "watt" in title_lower:
                w_index = title_lower.find("w")
                if w_index == -1:
                    w_index = title_lower.find("watt")
                
                if w_index > 0:
                    pre_text = title_lower[max(0, w_index - 5):w_index].strip()
                    if pre_text and pre_text[-1].isdigit():
                        for i in range(len(pre_text) - 1, -1, -1):
                            if not pre_text[i].isdigit():
                                wattage = pre_text[i+1:]
                                specs["wattage"] = f"{wattage}W"
                                break
            
            # Check certification
            for cert in ["80+ bronze", "80+ silver", "80+ gold", "80+ platinum", "80+ titanium"]:
                if cert in title_lower:
                    specs["certification"] = cert.upper()
                    break
            
            # Check if modular
            if "modular" in title_lower:
                if "semi" in title_lower:
                    specs["modular"] = "Semi"
                elif "full" in title_lower or "fully" in title_lower:
                    specs["modular"] = "Full"
                else:
                    specs["modular"] = "Yes"
        
        return specs
    
    def save_results(self, results):
        """
        Save scraped results to a file
        
        Args:
            results (dict): Dictionary of components by category
            
        Returns:
            str: Path to the saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"component_data_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        # Calculate total number of components
        total_components = sum(len(components) for components in results.values())
        
        # Create a structured output
        output = {
            "source": "Content-Aggregator",
            "scrape_date": datetime.now().isoformat(),
            "total_categories": len(results),
            "total_components": total_components,
            "categories": results
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved {total_components} components from {len(results)} categories to {filepath}")
        return filepath


def run_content_scraper(categories=None, search_terms=None, count_per_category=5):
    """
    Run the content scraper to fetch PC component data
    
    Args:
        categories (list): List of categories to fetch
        search_terms (dict): Dictionary mapping categories to search terms
        count_per_category (int): Number of components to fetch per category
        
    Returns:
        str: Path to the saved results file
    """
    scraper = ContentScraper()
    results = scraper.fetch_multiple_components(categories, search_terms, count_per_category)
    return scraper.save_results(results)


if __name__ == "__main__":
    # When run directly, fetch a sample of components from common categories
    common_categories = ['cpu', 'gpu', 'memory', 'storage', 'motherboard']
    run_content_scraper(categories=common_categories, count_per_category=3)