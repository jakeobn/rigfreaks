"""
Chillblast Product Scraper
A utility to scrape PC products from Chillblast.com
"""

import json
import re
import time
from datetime import datetime
import os
import trafilatura
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class ChillblastScraper:
    """Scraper class for Chillblast.com"""
    
    def __init__(self):
        # Base URL
        self.base_url = "https://www.chillblast.com"
        # Set headers to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://www.chillblast.com/',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        # Create a data directory if it doesn't exist
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_data')
        os.makedirs(self.data_dir, exist_ok=True)
        
    def fetch_page(self, url):
        """Fetch a page with error handling and rate limiting"""
        try:
            time.sleep(2)  # Rate limiting to be respectful
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error fetching {url}: Status code {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception fetching {url}: {str(e)}")
            return None
    
    def extract_product_links(self, category_url):
        """Extract product links from a category page"""
        html = self.fetch_page(category_url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        product_links = []
        
        # Look for product containers and extract links
        product_containers = soup.select('.product-item')
        for product in product_containers:
            link_element = product.select_one('a.product-item-title')
            if link_element and 'href' in link_element.attrs:
                href = link_element['href']
                if isinstance(href, str):
                    product_url = urljoin(self.base_url, href)
                    product_links.append(product_url)
        
        print(f"Found {len(product_links)} product links on {category_url}")
        return product_links
    
    def scrape_product_details(self, product_url):
        """Scrape details from a product page"""
        html = self.fetch_page(product_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Initialize product data
        product_data = {
            'url': product_url,
            'scraped_date': datetime.now().isoformat(),
            'components': {}
        }
        
        # Extract product title
        title_element = soup.select_one('h1.product-title')
        if title_element:
            product_data['title'] = title_element.text.strip()
        
        # Extract product price
        price_element = soup.select_one('.product-price .price')
        if price_element:
            price_text = price_element.text.strip()
            # Extract numbers from price text
            price_match = re.search(r'£([\d,]+\.?\d*)', price_text)
            if price_match:
                price = price_match.group(1).replace(',', '')
                product_data['price'] = float(price)
        
        # Extract product description
        description_element = soup.select_one('.product-description')
        if description_element:
            product_data['description'] = description_element.text.strip()
        
        # Extract specifications
        specs_container = soup.select_one('.product-specifications')
        if specs_container:
            spec_items = specs_container.select('.specification-item')
            for item in spec_items:
                label_element = item.select_one('.specification-label')
                value_element = item.select_one('.specification-value')
                
                if label_element and value_element:
                    label = label_element.text.strip().lower()
                    value = value_element.text.strip()
                    
                    # Map specifications to components
                    if 'processor' in label or 'cpu' in label:
                        product_data['components']['cpu'] = value
                    elif 'graphics' in label or 'gpu' in label:
                        product_data['components']['gpu'] = value
                    elif 'memory' in label or 'ram' in label:
                        product_data['components']['ram'] = value
                    elif 'storage' in label or 'ssd' in label or 'hard drive' in label:
                        product_data['components']['storage'] = value
                    elif 'motherboard' in label or 'mainboard' in label:
                        product_data['components']['motherboard'] = value
                    elif 'power supply' in label or 'psu' in label:
                        product_data['components']['power_supply'] = value
                    elif 'case' in label or 'chassis' in label:
                        product_data['components']['case'] = value
                    elif 'cooling' in label or 'cooler' in label:
                        product_data['components']['cooling'] = value
                    elif 'operating system' in label or 'os' in label:
                        product_data['components']['os'] = value
                    else:
                        # Store other specs in a general specs section
                        if 'specifications' not in product_data:
                            product_data['specifications'] = {}
                        product_data['specifications'][label] = value
        
        # Extract images
        image_elements = soup.select('.product-image-gallery img')
        if image_elements:
            product_data['images'] = []
            for img in image_elements:
                if 'src' in img.attrs:
                    src = img['src']
                    if isinstance(src, str):
                        img_url = urljoin(self.base_url, src)
                        product_data['images'].append(img_url)
        
        return product_data
    
    def scrape_category(self, category_url, category_name, limit=None):
        """Scrape all products from a category"""
        print(f"Scraping category: {category_name} from {category_url}")
        
        product_links = self.extract_product_links(category_url)
        if limit:
            product_links = product_links[:limit]
        
        products = []
        for i, product_url in enumerate(product_links):
            print(f"Scraping product {i+1}/{len(product_links)}: {product_url}")
            product_data = self.scrape_product_details(product_url)
            if product_data:
                product_data['category'] = category_name
                products.append(product_data)
        
        # Save the scraped data to a JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.data_dir, f'chillblast_{category_name.lower()}_{timestamp}.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({'products': products}, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(products)} products to {filename}")
        return products
    
    def scrape_categories(self, categories, limit_per_category=None):
        """Scrape products from multiple categories"""
        all_products = []
        for category_name, category_url in categories.items():
            products = self.scrape_category(category_url, category_name, limit_per_category)
            all_products.extend(products)
        
        # Save all products to a combined file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.data_dir, f'chillblast_all_products_{timestamp}.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({'products': all_products}, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(all_products)} products in total to {filename}")
        return all_products
    
    def scrape_main_categories(self, limit_per_category=5):
        """Scrape main product categories from Chillblast"""
        categories = {
            'Gaming_PCs': 'https://www.chillblast.com/gaming-pcs',
            'Custom_PCs': 'https://www.chillblast.com/custom-pcs',
            'Workstations': 'https://www.chillblast.com/workstations'
        }
        
        return self.scrape_categories(categories, limit_per_category)

def run_scraper(limit_per_category=5):
    """Run the scraper with the specified limit per category"""
    scraper = ChillblastScraper()
    return scraper.scrape_main_categories(limit_per_category)

if __name__ == "__main__":
    # Run the scraper with a limit of 5 products per category
    run_scraper(5)