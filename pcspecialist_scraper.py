"""
PCSpecialist UK Data Provider
A utility to fetch PC component data from PCSpecialist UK
"""
import os
import json
import time
import logging
import random
import requests
from datetime import datetime
from bs4 import BeautifulSoup


class PCSpecialistProvider:
    """Data Provider for PCSpecialist UK"""
    
    BASE_URL = "https://www.pcspecialist.co.uk"
    
    # Component categories
    CATEGORIES = {
        "cpu": {"path": "/computers/processors", "name": "CPUs"},
        "cpu_cooler": {"path": "/computers/cooling", "name": "CPU Coolers"},
        "motherboard": {"path": "/computers/motherboards", "name": "Motherboards"},
        "memory": {"path": "/computers/memory", "name": "Memory"},
        "storage": {"path": "/computers/hard-drives", "name": "Storage"},
        "gpu": {"path": "/computers/graphics-cards", "name": "Graphics Cards"},
        "case": {"path": "/computers/cases", "name": "Cases"},
        "power_supply": {"path": "/computers/power-supplies", "name": "Power Supplies"},
        "operating_system": {"path": "/computers/software", "name": "Operating Systems"},
        "monitor": {"path": "/computers/monitors", "name": "Monitors"},
        "case_fan": {"path": "/computers/case-fans", "name": "Case Fans"}
    }
    
    # Common filters by category (will be updated based on PCSpecialist's structure)
    FILTERS = {
        "cpu": {
            "manufacturer": ["AMD", "Intel"],
            "socket": ["AM4", "AM5", "LGA1700", "LGA1200", "TR4"],
        },
        "gpu": {
            "manufacturer": ["AMD", "NVIDIA", "Intel"],
        },
        "memory": {
            "type": ["DDR4", "DDR5"],
            "capacity": ["8 GB", "16 GB", "32 GB", "64 GB", "128 GB"],
        },
        "motherboard": {
            "socket": ["AM4", "AM5", "LGA1700", "LGA1200", "TR4"],
            "form_factor": ["ATX", "Micro ATX", "Mini ITX"],
        },
        "storage": {
            "type": ["SSD", "HDD", "M.2 SSD", "NVMe"],
            "capacity": ["250 GB", "500 GB", "1 TB", "2 TB", "4 TB", "8 TB"],
        }
    }
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.google.com/",
        "Sec-Ch-Ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
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
        
        # Initialize session with headers
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def get_available_filters(self, category):
        """Get available filters for a category"""
        if category in self.FILTERS:
            return self.FILTERS[category]
        return {}
    
    def get_categories(self):
        """Get available categories"""
        return {category: info for category, info in self.CATEGORIES.items()}
    
    def fetch_product_data(self, categories=None, filters=None, count_per_category=10):
        """Fetch product data from PCSpecialist UK with optional filters"""
        results = {}
        
        # If no categories specified, use all categories
        if not categories:
            categories = list(self.CATEGORIES.keys())
            
        # Ensure categories is a list
        if isinstance(categories, str):
            categories = [categories]
        
        for category in categories:
            if category not in self.CATEGORIES:
                self.logger.warning(f"Skipping invalid category: {category}")
                continue
                
            self.logger.info(f"Fetching data for category: {category}")
            
            # Get filters for this category if provided
            category_filters = filters.get(category, {}) if filters else None
            
            # Scrape data from PCSpecialist UK
            products = self._scrape_category_products(category, count_per_category, category_filters)
            results[category] = products
            
            # Add a short delay to avoid hitting the site too quickly
            time.sleep(1.5 + random.random())
        
        return results
        
    def _scrape_category_products(self, category, limit=10, filters=None):
        """Scrape products from a specific category on PCSpecialist UK"""
        if category not in self.CATEGORIES:
            self.logger.error(f"Invalid category: {category}")
            return []
            
        category_info = self.CATEGORIES[category]
        category_path = category_info["path"]
        
        # Construct URL
        url = f"{self.BASE_URL}{category_path}"
        
        # Get the page content with robust error handling
        max_retries = 3
        retry_count = 0
        products = []
        
        while retry_count < max_retries and not products:
            try:
                # Add a random delay between requests
                time.sleep(2 + random.random() * 2)
                
                self.logger.debug(f"Fetching URL: {url}")
                response = self.session.get(
                    url, 
                    timeout=15,
                    allow_redirects=True
                )
                
                # Log response details for debugging
                self.logger.debug(f"Response status: {response.status_code}")
                
                if response.status_code == 403:
                    self.logger.warning("Received 403 Forbidden. This may indicate anti-scraping measures.")
                    retry_count += 1
                    continue
                    
                response.raise_for_status()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract products
                # For PCSpecialist, we need to find the right selectors for products
                # This will vary based on their site structure
                product_elements = []
                
                # Try different selectors based on the category
                selectors = [
                    '.products-list .product-item',  # Common product item selector
                    '.product-item-info',            # Another common pattern
                    '.prod-item',                    # Simple class name
                    '.item.product',                 # Bootstrap-style naming
                    'div[data-role="product-item"]', # Data attribute based selector
                    '.box-product',                  # Another common class
                ]
                
                for selector in selectors:
                    found_elements = soup.select(selector)
                    if found_elements:
                        product_elements = found_elements
                        self.logger.debug(f"Found product elements with selector: {selector}")
                        break
                
                self.logger.debug(f"Found {len(product_elements)} product elements on the page")
                
                # If we find no products, try to detect patterns in the page
                if not product_elements:
                    # Look for any product-like structures
                    possible_elements = soup.find_all(['div', 'li'], class_=lambda x: x and ('product' in x.lower() or 'item' in x.lower()))
                    if possible_elements:
                        product_elements = possible_elements[:limit]
                        self.logger.debug("Found potential product elements using fallback detection")
                
                # Limit the number of products
                counter = 0
                for product_el in product_elements:
                    if counter >= limit:
                        break
                        
                    product_data = self._parse_product_element(product_el, category, soup)
                    if product_data:
                        products.append(product_data)
                        counter += 1
                
                if products:
                    return products
                else:
                    self.logger.warning(f"No products found on page for category {category}. Retrying...")
                    retry_count += 1
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error scraping {category} products: {str(e)}")
                retry_count += 1
                time.sleep(5)  # Longer delay after an error
            except Exception as e:
                self.logger.error(f"Error scraping {category} products: {str(e)}")
                retry_count += 1
        
        # If scraping failed, provide informative error
        if not products:
            self.logger.error(f"All scraping attempts failed for {category} on PCSpecialist UK.")
            
        return products
    
    def _parse_product_element(self, product_el, category, page_soup):
        """Parse a product element from PCSpecialist search results"""
        try:
            # Extract basic product info
            product = {"category": category}
            
            # Get name - try different selectors
            name_el = (
                product_el.select_one('.product-name') or 
                product_el.select_one('.product-title') or
                product_el.select_one('.product-item-name') or
                product_el.select_one('h2, h3, h4') or
                product_el.select_one('a[title]')
            )
            
            if name_el:
                if name_el.name == 'a' and name_el.has_attr('title'):
                    product["name"] = name_el['title'].strip()
                else:
                    product["name"] = name_el.text.strip()
                
                # Find URL
                url_el = name_el if name_el.name == 'a' else product_el.select_one('a')
                if url_el and url_el.has_attr('href'):
                    url = url_el['href']
                    if not url.startswith('http'):
                        url = self.BASE_URL + url if not url.startswith('/') else self.BASE_URL + url
                    product["url"] = url
            else:
                # Try to extract name from any heading or link text
                heading = product_el.select_one('h1, h2, h3, h4, h5, a')
                if heading:
                    product["name"] = heading.text.strip()
                else:
                    return None  # Skip if no name found
            
            # Get price - try different selectors
            price_el = (
                product_el.select_one('.price') or
                product_el.select_one('.product-price') or
                product_el.select_one('.price-box') or
                product_el.select_one('[data-price]')
            )
            
            if price_el:
                # Extract the price text
                price_text = price_el.text.strip()
                # Remove currency symbol and convert to float
                price_text = price_text.replace('£', '').replace('$', '').replace('€', '').replace(',', '').strip()
                # Extract just the numbers and decimal point
                import re
                price_match = re.search(r'\d+(\.\d+)?', price_text)
                if price_match:
                    try:
                        product["price"] = float(price_match.group(0))
                    except ValueError:
                        product["price"] = 0.0
            
            # Get image URL
            img_el = product_el.select_one('img')
            if img_el and img_el.has_attr('src'):
                src = img_el['src']
                if not src.startswith('http'):
                    src = self.BASE_URL + src if not src.startswith('/') else self.BASE_URL + src
                product["image_url"] = src
            elif img_el and img_el.has_attr('data-src'):
                src = img_el['data-src']
                if not src.startswith('http'):
                    src = self.BASE_URL + src if not src.startswith('/') else self.BASE_URL + src
                product["image_url"] = src
            
            # Extract specifications based on category
            if category == "cpu":
                product.update(self._extract_cpu_specs(product_el, page_soup))
            elif category == "gpu":
                product.update(self._extract_gpu_specs(product_el, page_soup))
            elif category == "memory":
                product.update(self._extract_memory_specs(product_el, page_soup))
            elif category == "storage":
                product.update(self._extract_storage_specs(product_el, page_soup))
            elif category == "motherboard":
                product.update(self._extract_motherboard_specs(product_el, page_soup))
            
            # Add a unique ID
            import hashlib
            product["id"] = hashlib.md5(product["name"].encode()).hexdigest()
            
            return product
            
        except Exception as e:
            self.logger.error(f"Error parsing product element: {str(e)}")
            return None
    
    def _extract_cpu_specs(self, product_el, page_soup):
        """Extract CPU specifications"""
        specs = {}
        
        # Look for CPU specs in various formats
        spec_elements = product_el.select('.product-specs li, .specifications li, .specs li, .description li')
        
        for spec in spec_elements:
            text = spec.text.strip().lower()
            
            if 'core' in text and 'cores' in text:
                import re
                cores_match = re.search(r'(\d+)\s*cores', text)
                if cores_match:
                    specs["cores"] = cores_match.group(1)
            
            if 'frequency' in text or 'ghz' in text or 'clock' in text:
                import re
                freq_match = re.search(r'([\d\.]+)\s*ghz', text)
                if freq_match:
                    specs["frequency"] = f"{freq_match.group(1)} GHz"
            
            if 'tdp' in text or 'watt' in text or 'power' in text:
                import re
                tdp_match = re.search(r'(\d+)\s*w', text)
                if tdp_match:
                    specs["tdp"] = f"{tdp_match.group(1)}W"
            
            if 'socket' in text:
                if 'am4' in text:
                    specs["socket"] = "AM4"
                elif 'am5' in text:
                    specs["socket"] = "AM5"
                elif 'lga1700' in text or 'lga 1700' in text:
                    specs["socket"] = "LGA1700"
                elif 'lga1200' in text or 'lga 1200' in text:
                    specs["socket"] = "LGA1200"
            
            if 'amd' in text:
                specs["manufacturer"] = "AMD"
            elif 'intel' in text:
                specs["manufacturer"] = "Intel"
        
        return specs
    
    def _extract_gpu_specs(self, product_el, page_soup):
        """Extract GPU specifications"""
        specs = {}
        
        # Look for GPU specs in various formats
        spec_elements = product_el.select('.product-specs li, .specifications li, .specs li, .description li')
        
        for spec in spec_elements:
            text = spec.text.strip().lower()
            
            if 'memory' in text or 'vram' in text or 'gb' in text:
                import re
                mem_match = re.search(r'(\d+)\s*gb', text)
                if mem_match:
                    specs["memory"] = f"{mem_match.group(1)} GB"
            
            if 'clock' in text or 'mhz' in text or 'ghz' in text:
                import re
                clock_match = re.search(r'([\d\.]+)\s*ghz', text) or re.search(r'([\d\.]+)\s*mhz', text)
                if clock_match:
                    value = float(clock_match.group(1))
                    unit = "GHz" if "ghz" in text or value < 100 else "MHz"
                    specs["core_clock"] = f"{value} {unit}"
            
            if 'nvidia' in text or 'geforce' in text or 'rtx' in text or 'gtx' in text:
                specs["manufacturer"] = "NVIDIA"
                
                # Try to extract chipset
                import re
                chipset_match = re.search(r'(rtx\s*\d+\s*[a-z]*|gtx\s*\d+\s*[a-z]*)', text)
                if chipset_match:
                    chipset = chipset_match.group(1).upper().replace(' ', ' ')
                    specs["chipset"] = f"GeForce {chipset}"
                
            elif 'amd' in text or 'radeon' in text or 'rx' in text:
                specs["manufacturer"] = "AMD"
                
                # Try to extract chipset
                import re
                chipset_match = re.search(r'(rx\s*\d+\s*[a-z]*)', text)
                if chipset_match:
                    chipset = chipset_match.group(1).upper().replace(' ', ' ')
                    specs["chipset"] = f"Radeon {chipset}"
        
        return specs
    
    def _extract_memory_specs(self, product_el, page_soup):
        """Extract memory specifications"""
        specs = {}
        
        # Look for memory specs in various formats
        spec_elements = product_el.select('.product-specs li, .specifications li, .specs li, .description li')
        
        for spec in spec_elements:
            text = spec.text.strip().lower()
            
            if 'capacity' in text or 'gb' in text:
                import re
                cap_match = re.search(r'(\d+)\s*gb', text)
                if cap_match:
                    specs["capacity"] = f"{cap_match.group(1)} GB"
            
            if 'speed' in text or 'mhz' in text or 'frequency' in text:
                import re
                speed_match = re.search(r'(\d+)\s*mhz', text)
                if speed_match:
                    specs["speed"] = speed_match.group(1)
            
            if 'ddr4' in text:
                specs["type"] = "DDR4"
            elif 'ddr5' in text:
                specs["type"] = "DDR5"
        
        return specs
    
    def _extract_storage_specs(self, product_el, page_soup):
        """Extract storage specifications"""
        specs = {}
        
        # Look for storage specs in various formats
        spec_elements = product_el.select('.product-specs li, .specifications li, .specs li, .description li')
        
        for spec in spec_elements:
            text = spec.text.strip().lower()
            
            if 'capacity' in text or 'gb' in text or 'tb' in text:
                import re
                tb_match = re.search(r'(\d+)\s*tb', text)
                gb_match = re.search(r'(\d+)\s*gb', text)
                
                if tb_match:
                    specs["capacity"] = f"{tb_match.group(1)} TB"
                elif gb_match:
                    gb = int(gb_match.group(1))
                    if gb >= 1000:
                        specs["capacity"] = f"{gb/1000} TB"
                    else:
                        specs["capacity"] = f"{gb} GB"
            
            if 'ssd' in text:
                if 'nvme' in text or 'm.2' in text or 'pcie' in text:
                    specs["type"] = "NVMe SSD"
                else:
                    specs["type"] = "SSD"
            elif 'hdd' in text:
                specs["type"] = "HDD"
            
            if 'interface' in text or 'connection' in text:
                if 'sata' in text:
                    specs["interface"] = "SATA"
                elif 'pcie' in text or 'pci-e' in text:
                    if 'gen 4' in text or 'gen4' in text:
                        specs["interface"] = "PCIe 4.0 x4"
                    elif 'gen 3' in text or 'gen3' in text:
                        specs["interface"] = "PCIe 3.0 x4"
                    else:
                        specs["interface"] = "PCIe"
        
        return specs
    
    def _extract_motherboard_specs(self, product_el, page_soup):
        """Extract motherboard specifications"""
        specs = {}
        
        # Look for motherboard specs in various formats
        spec_elements = product_el.select('.product-specs li, .specifications li, .specs li, .description li')
        
        for spec in spec_elements:
            text = spec.text.strip().lower()
            
            if 'socket' in text:
                if 'am4' in text:
                    specs["socket"] = "AM4"
                elif 'am5' in text:
                    specs["socket"] = "AM5"
                elif 'lga1700' in text or 'lga 1700' in text:
                    specs["socket"] = "LGA1700"
                elif 'lga1200' in text or 'lga 1200' in text:
                    specs["socket"] = "LGA1200"
            
            if 'chipset' in text:
                if 'x570' in text:
                    specs["chipset"] = "X570"
                elif 'b550' in text:
                    specs["chipset"] = "B550"
                elif 'x670' in text:
                    specs["chipset"] = "X670"
                elif 'b650' in text:
                    specs["chipset"] = "B650"
                elif 'z690' in text:
                    specs["chipset"] = "Z690"
                elif 'z790' in text:
                    specs["chipset"] = "Z790"
                elif 'b760' in text:
                    specs["chipset"] = "B760"
            
            if 'form factor' in text or 'form-factor' in text or 'size' in text:
                if 'atx' in text and 'micro' not in text and 'mini' not in text:
                    specs["form_factor"] = "ATX"
                elif 'micro' in text or 'matx' in text or 'microatx' in text:
                    specs["form_factor"] = "Micro ATX"
                elif 'mini' in text or 'mitx' in text or 'mini-itx' in text:
                    specs["form_factor"] = "Mini ITX"
        
        return specs
    
    def save_results(self, results):
        """Save results to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pcspecialist_uk_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        # Calculate total number of products
        total_products = sum(len(products) for products in results.values())
        
        # Create a structured output
        output = {
            "source": "PCSpecialist UK",
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


def run_pcspecialist_data_provider(categories=None, filters=None, count_per_category=10):
    """Run the PCSpecialist UK data provider with specified parameters"""
    provider = PCSpecialistProvider()
    results = provider.fetch_product_data(categories, filters, count_per_category)
    return provider.save_results(results)


if __name__ == "__main__":
    # When run directly, fetch a sample of products from common categories
    common_categories = ['cpu', 'gpu', 'memory', 'storage', 'motherboard']
    run_pcspecialist_data_provider(categories=common_categories, count_per_category=5)