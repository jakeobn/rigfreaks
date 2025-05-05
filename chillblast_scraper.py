"""Chillblast website scraper module

This module provides utilities for scraping product data and images from the Chillblast website
to ensure our redesign accurately represents their design and content structure.
"""

import os
import time
import requests
import json
import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

# Base URLs
BASE_URL = "https://www.chillblast.com"
GAMING_PC_URL = "https://www.chillblast.com/gaming-pcs"
WORKSTATION_URL = "https://www.chillblast.com/workstations"

# Output directories
DATA_DIR = "scraped_data"
IMAGES_DIR = os.path.join("static", "images", "chillblast")

# Ensure directories exist
def ensure_dirs():
    """Create necessary directories if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

def get_html_content(url):
    """Fetch HTML content from URL using Trafilatura for robustness."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            return downloaded
        else:
            # Fallback to regular requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def extract_product_details(product_url):
    """Extract detailed information about a product."""
    html_content = get_html_content(product_url)
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract product data
    product = {}
    
    # Basic info
    product['url'] = product_url
    product['name'] = soup.select_one('h1.page-title span').text.strip() if soup.select_one('h1.page-title span') else ''
    
    # Price
    price_elem = soup.select_one('span.price')
    if price_elem:
        price_text = price_elem.text.strip()
        # Remove currency symbol and commas, convert to float
        price_text = price_text.replace('£', '').replace(',', '')
        try:
            product['price'] = float(price_text)
        except ValueError:
            product['price'] = 0.0
    else:
        product['price'] = 0.0
    
    # Description
    description_elem = soup.select_one('div.product.attribute.description div.value')
    product['description'] = description_elem.text.strip() if description_elem else ''
    
    # Specifications
    specs = {}
    specs_table = soup.select('table.data.table.additional-attributes tbody tr')
    for row in specs_table:
        key_elem = row.select_one('th.col.label')
        value_elem = row.select_one('td.col.data')
        if key_elem and value_elem:
            key = key_elem.text.strip()
            value = value_elem.text.strip()
            specs[key] = value
    
    product['specifications'] = specs
    
    # Main image URL
    main_image = soup.select_one('img.gallery-placeholder__image')
    if main_image and 'src' in main_image.attrs:
        product['main_image_url'] = main_image['src']
        # Download the image
        download_image(product['main_image_url'], f"{slugify(product['name'])}_main.jpg")
    else:
        product['main_image_url'] = ''
    
    # Gallery images
    gallery_images = soup.select('img.fotorama__img')
    product['gallery_images'] = []
    for i, img in enumerate(gallery_images):
        if 'src' in img.attrs:
            img_url = img['src']
            product['gallery_images'].append(img_url)
            # Download gallery image
            download_image(img_url, f"{slugify(product['name'])}_gallery_{i}.jpg")
    
    return product

def download_image(url, filename):
    """Download image and save to images directory."""
    try:
        if not url.startswith('http'):
            url = urljoin(BASE_URL, url)
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        file_path = os.path.join(IMAGES_DIR, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded image: {filename}")
        return file_path
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return None

def slugify(text):
    """Convert text to slug format for filenames."""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text

def scrape_product_list(url, category):
    """Scrape product listings from a category page."""
    html_content = get_html_content(url)
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    products = []
    product_items = soup.select('ol.products.list.items.product-items li.product-item')
    
    for item in product_items:
        product = {}
        
        # Product link
        link_elem = item.select_one('a.product-item-link')
        if link_elem and 'href' in link_elem.attrs:
            product['url'] = link_elem['href']
            product['name'] = link_elem.text.strip()
        else:
            continue
        
        # Price
        price_elem = item.select_one('span.price')
        if price_elem:
            price_text = price_elem.text.strip()
            price_text = price_text.replace('£', '').replace(',', '')
            try:
                product['price'] = float(price_text)
            except ValueError:
                product['price'] = 0.0
        else:
            product['price'] = 0.0
        
        # Image
        img_elem = item.select_one('img.product-image-photo')
        if img_elem and 'src' in img_elem.attrs:
            product['image_url'] = img_elem['src']
            # Download thumbnail image
            download_image(product['image_url'], f"{slugify(product['name'])}_thumb.jpg")
        else:
            product['image_url'] = ''
        
        # Category
        product['category'] = category
        
        products.append(product)
    
    return products

def scrape_all_products():
    """Scrape products from all categories and save data."""
    ensure_dirs()
    
    # Get gaming PCs
    print("Scraping gaming PCs...")
    gaming_pcs = scrape_product_list(GAMING_PC_URL, 'gaming')
    
    # Get workstations
    print("Scraping workstations...")
    workstations = scrape_product_list(WORKSTATION_URL, 'workstation')
    
    # Combine all products
    all_products = gaming_pcs + workstations
    
    # Get detailed information for each product (limit to 5 for demonstration)
    detailed_products = []
    for i, product in enumerate(all_products[:5]):
        print(f"Scraping details for {product['name']}...")
        detailed_product = extract_product_details(product['url'])
        if detailed_product:
            detailed_products.append(detailed_product)
        # Be nice to the server
        time.sleep(2)
    
    # Save to JSON file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(os.path.join(DATA_DIR, f"chillblast_products_{timestamp}.json"), 'w') as f:
        json.dump(detailed_products, f, indent=2)
    
    with open(os.path.join(DATA_DIR, f"chillblast_products_list_{timestamp}.json"), 'w') as f:
        json.dump(all_products, f, indent=2)
    
    print(f"Scraped {len(all_products)} products, saved {len(detailed_products)} with full details")
    return all_products, detailed_products

def scrape_layout_patterns():
    """Analyze and extract layout patterns from Chillblast website."""
    # Homepage layout
    homepage_html = get_html_content(BASE_URL)
    if homepage_html:
        # Save raw HTML for reference
        with open(os.path.join(DATA_DIR, "chillblast_homepage.html"), 'w') as f:
            f.write(homepage_html)
        
        # Extract layout patterns
        soup = BeautifulSoup(homepage_html, 'html.parser')
        
        # Header structure
        header = soup.select_one('header.page-header')
        if header:
            with open(os.path.join(DATA_DIR, "chillblast_header.html"), 'w') as f:
                f.write(str(header))
        
        # Footer structure
        footer = soup.select_one('footer.page-footer')
        if footer:
            with open(os.path.join(DATA_DIR, "chillblast_footer.html"), 'w') as f:
                f.write(str(footer))
        
        # Main content sections
        main_content = soup.select_one('main#maincontent')
        if main_content:
            with open(os.path.join(DATA_DIR, "chillblast_main_content.html"), 'w') as f:
                f.write(str(main_content))
    
    print("Layout patterns extracted and saved")

def extract_design_assets():
    """Extract design assets like logos, icons, and color schemes."""
    homepage_html = get_html_content(BASE_URL)
    if not homepage_html:
        return
    
    soup = BeautifulSoup(homepage_html, 'html.parser')
    
    # Extract logo
    logo = soup.select_one('a.logo img')
    if logo and 'src' in logo.attrs:
        download_image(logo['src'], "chillblast_logo.png")
    
    # Extract CSS to analyze color scheme
    css_links = soup.select('link[rel="stylesheet"]')
    css_urls = [link['href'] for link in css_links if 'href' in link.attrs]
    
    for i, css_url in enumerate(css_urls):
        try:
            if not css_url.startswith('http'):
                css_url = urljoin(BASE_URL, css_url)
            
            response = requests.get(css_url)
            if response.status_code == 200:
                with open(os.path.join(DATA_DIR, f"chillblast_css_{i}.css"), 'w') as f:
                    f.write(response.text)
        except Exception as e:
            print(f"Error downloading CSS {css_url}: {e}")
    
    print("Design assets extracted")

def main():
    """Main function to run the scraper."""
    print("Starting Chillblast scraper...")
    ensure_dirs()
    
    # Scrape layout patterns first
    print("Extracting layout patterns...")
    scrape_layout_patterns()
    
    # Extract design assets
    print("Extracting design assets...")
    extract_design_assets()
    
    # Scrape products
    print("Scraping products...")
    all_products, detailed_products = scrape_all_products()
    
    print("Scraping complete!")
    return {
        "products": len(all_products),
        "detailed_products": len(detailed_products)
    }

if __name__ == "__main__":
    main()
