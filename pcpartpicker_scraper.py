"""
PCPartPicker UK Scraper
A utility to scrape PC component data from pcpartpicker.co.uk
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


class PCPartPickerScraper:
    """Scraper class for PCPartPicker UK"""
    
    BASE_URL = "https://uk.pcpartpicker.com"
    CATEGORIES = {
        "cpu": "/products/cpu/",
        "cpu_cooler": "/products/cpu-cooler/",
        "motherboard": "/products/motherboard/",
        "memory": "/products/memory/",
        "storage": "/products/internal-hard-drive/",
        "gpu": "/products/video-card/",
        "case": "/products/case/",
        "power_supply": "/products/power-supply/",
        "operating_system": "/products/os/",
        "monitor": "/products/monitor/",
        "case_fan": "/products/case-fan/"
    }
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    def __init__(self):
        """Initialize the scraper with data directory"""
        # Setup data directory
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def fetch_page(self, url):
        """Fetch a page with error handling and rate limiting"""
        self.logger.info(f"Fetching: {url}")
        
        try:
            # Random delay between requests to avoid being blocked
            time.sleep(random.uniform(0.5, 2))
            
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_category_page(self, html, category):
        """Parse the category page to extract product listings"""
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find all product rows in the table
        product_rows = soup.select('tr.tr__product')
        
        for row in product_rows:
            try:
                # Extract product details
                name_elem = row.select_one('.td__nameWrapper a')
                if not name_elem:
                    continue
                    
                name = name_elem.text.strip()
                product_url = self.BASE_URL + name_elem['href'] if name_elem.has_attr('href') else ""
                
                # Extract price
                price_elem = row.select_one('.td__price')
                price = None
                if price_elem:
                    price_text = price_elem.text.strip()
                    # Convert "£123.45" to 123.45
                    if price_text and price_text != "":
                        try:
                            price = float(price_text.replace('£', '').replace(',', ''))
                        except ValueError:
                            price = None
                
                # Extract image
                img_elem = row.select_one('.td__image img')
                image_url = img_elem['src'] if img_elem and img_elem.has_attr('src') else None
                
                # Extract rating if available
                rating_elem = row.select_one('.td__rating')
                rating = rating_elem.text.strip() if rating_elem else None
                
                # Extract specs based on category
                specs = self.extract_specs(row, category)
                
                products.append({
                    'name': name,
                    'url': product_url,
                    'price': price,
                    'image_url': image_url,
                    'category': category,
                    'rating': rating,
                    'specs': specs
                })
                
            except Exception as e:
                self.logger.error(f"Error parsing product row: {e}")
                continue
                
        return products
    
    def extract_specs(self, row, category):
        """Extract category-specific specifications from a product row"""
        specs = {}
        
        # Common spec extraction
        specs_elements = row.select('.td__spec')
        
        # Extract specs based on category
        if category == 'cpu':
            # CPUs typically have cores, frequency, socket
            if len(specs_elements) >= 3:
                specs['cores'] = specs_elements[0].text.strip() if specs_elements[0] else None
                specs['frequency'] = specs_elements[1].text.strip() if specs_elements[1] else None
                specs['socket'] = specs_elements[2].text.strip() if specs_elements[2] else None
                
        elif category == 'gpu':
            # GPUs typically have chipset, memory, core clock
            if len(specs_elements) >= 3:
                specs['chipset'] = specs_elements[0].text.strip() if specs_elements[0] else None
                specs['memory'] = specs_elements[1].text.strip() if specs_elements[1] else None
                specs['core_clock'] = specs_elements[2].text.strip() if specs_elements[2] else None
                
        elif category == 'memory':
            # RAM typically has speed, size, type
            if len(specs_elements) >= 3:
                specs['speed'] = specs_elements[0].text.strip() if specs_elements[0] else None
                specs['size'] = specs_elements[1].text.strip() if specs_elements[1] else None
                specs['type'] = specs_elements[2].text.strip() if specs_elements[2] else None
                
        elif category == 'storage':
            # Storage typically has capacity, type, cache
            if len(specs_elements) >= 3:
                specs['capacity'] = specs_elements[0].text.strip() if specs_elements[0] else None
                specs['type'] = specs_elements[1].text.strip() if specs_elements[1] else None
                specs['cache'] = specs_elements[2].text.strip() if specs_elements[2] else None
                
        elif category == 'motherboard':
            # Motherboards typically have socket, form factor, RAM slots
            if len(specs_elements) >= 3:
                specs['socket'] = specs_elements[0].text.strip() if specs_elements[0] else None
                specs['form_factor'] = specs_elements[1].text.strip() if specs_elements[1] else None
                specs['ram_slots'] = specs_elements[2].text.strip() if specs_elements[2] else None
                
        elif category == 'power_supply':
            # PSUs typically have wattage, modular status, efficiency
            if len(specs_elements) >= 3:
                specs['wattage'] = specs_elements[0].text.strip() if specs_elements[0] else None
                specs['modular'] = specs_elements[1].text.strip() if specs_elements[1] else None
                specs['efficiency'] = specs_elements[2].text.strip() if specs_elements[2] else None
                
        elif category == 'case':
            # Cases typically have type, color, side panel
            if len(specs_elements) >= 3:
                specs['type'] = specs_elements[0].text.strip() if specs_elements[0] else None
                specs['color'] = specs_elements[1].text.strip() if specs_elements[1] else None
                specs['side_panel'] = specs_elements[2].text.strip() if specs_elements[2] else None
        
        # For other categories, just extract all available specs
        else:
            for i, spec in enumerate(specs_elements):
                specs[f'spec_{i+1}'] = spec.text.strip()
                
        return specs
    
    def scrape_product_details(self, url):
        """Scrape detailed information from a product page"""
        if not url:
            return {}
            
        html = self.fetch_page(url)
        if not html:
            return {}
            
        soup = BeautifulSoup(html, 'html.parser')
        details = {}
        
        # Extract product name
        name_elem = soup.select_one('h1.pageTitle')
        details['full_name'] = name_elem.text.strip() if name_elem else None
        
        # Extract product images
        image_containers = soup.select('.productImageContainer img')
        details['images'] = [img['src'] for img in image_containers if img.has_attr('src')]
        
        # Extract price
        price_elem = soup.select_one('.price__finalValue')
        if price_elem:
            price_text = price_elem.text.strip()
            try:
                details['current_price'] = float(price_text.replace('£', '').replace(',', ''))
            except ValueError:
                details['current_price'] = None
        
        # Extract specifications
        specs_table = soup.select('.specs table tr')
        specifications = {}
        
        for row in specs_table:
            header = row.select_one('td.td__header, th.td__header')
            data = row.select_one('td.td__data')
            
            if header and data:
                header_text = header.text.strip()
                data_text = data.text.strip()
                specifications[header_text] = data_text
                
        details['specifications'] = specifications
        
        # Extract description using trafilatura if available
        try:
            description = trafilatura.extract(html, include_comments=False, 
                                            include_tables=False, 
                                            include_links=False)
            details['description'] = description
        except:
            # Fallback to a simple extraction
            description_elem = soup.select_one('.product__description')
            details['description'] = description_elem.text.strip() if description_elem else None
            
        return details
    
    def scrape_category(self, category, limit=None, get_details=False):
        """Scrape all products from a category"""
        if category not in self.CATEGORIES:
            self.logger.error(f"Invalid category: {category}")
            return []
            
        url = self.BASE_URL + self.CATEGORIES[category]
        html = self.fetch_page(url)
        
        if not html:
            return []
            
        # Parse the category page to get product listings
        products = self.parse_category_page(html, category)
        
        # Apply limit if specified
        if limit and len(products) > limit:
            products = products[:limit]
            
        # Get detailed information for each product if requested
        if get_details:
            for product in products:
                if product.get('url'):
                    details = self.scrape_product_details(product['url'])
                    product.update(details)
                    
                    # Add a small delay between requests
                    time.sleep(random.uniform(0.5, 1.5))
                    
        return products
    
    def scrape_categories(self, categories=None, limit_per_category=5, get_details=False):
        """Scrape products from multiple categories"""
        results = {}
        
        # If no categories specified, use all categories
        if not categories:
            categories = list(self.CATEGORIES.keys())
            
        # Ensure categories is a list
        if isinstance(categories, str):
            categories = [categories]
            
        for category in categories:
            self.logger.info(f"Scraping category: {category}")
            products = self.scrape_category(category, limit=limit_per_category, get_details=get_details)
            results[category] = products
            
        return results
    
    def save_results(self, results):
        """Save scraped results to a file"""
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


def run_scraper(categories=None, limit_per_category=5, get_details=False):
    """Run the PCPartPicker UK scraper with specified parameters"""
    scraper = PCPartPickerScraper()
    results = scraper.scrape_categories(categories, limit_per_category, get_details)
    return scraper.save_results(results)


if __name__ == "__main__":
    # When run directly, scrape all categories with limit of 5 products each
    run_scraper(limit_per_category=5)