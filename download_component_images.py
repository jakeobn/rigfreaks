"""Download PC component images from Chillblast website.

This script downloads specific PC component images from Chillblast's website to use
in our PC builder. It targets high-quality product images of components like CPUs,
motherboards, RAM, etc.
"""

import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URLs
BASE_URL = "https://www.chillblast.com"
COMPONENT_PAGES = {
    "cpu": [
        "https://www.chillblast.com/intel-core-i9-14900k-processor-retail.html",
        "https://www.chillblast.com/intel-core-i7-14700k-processor-retail.html",
        "https://www.chillblast.com/intel-core-i5-14600k-processor-retail.html",
        "https://www.chillblast.com/amd-ryzen-9-7950x3d-processor-12.html",
        "https://www.chillblast.com/amd-ryzen-7-7800x3d-processor.html",
    ],
    "motherboard": [
        "https://www.chillblast.com/asus-rog-strix-z790-f-gaming-wifi-7-7.html",
        "https://www.chillblast.com/asus-rog-strix-b760-f-gaming-wifi.html",
        "https://www.chillblast.com/asus-tuf-gaming-b650-plus-wifi.html",
        "https://www.chillblast.com/gigabyte-z790-aorus-elite-ax-motherboard.html",
        "https://www.chillblast.com/gigabyte-b650-gaming-x-ax-motherboard.html",
    ],
    "ram": [
        "https://www.chillblast.com/kingston-fury-beast-rgb-ddr5-32gb-6000mt-s-cl36-41.html",
        "https://www.chillblast.com/corsair-vengeance-rgb-pro-sl-32gb-ddr4-3600mhz-cl18-9.html",
        "https://www.chillblast.com/corsair-vengeance-ddr5-32gb-5600mt-s-cl36-15.html",
        "https://www.chillblast.com/corsair-vengeance-rgb-ddr5-32gb-5600mt-s-cl40-0.html",
    ],
    "gpu": [
        "https://www.chillblast.com/gigabyte-geforce-rtx-4090-gaming-oc-24g-18.html",
        "https://www.chillblast.com/asus-tuf-gaming-geforce-rtx-4080-super-16g-gaming.html",
        "https://www.chillblast.com/asus-dual-geforce-rtx-4070-ti-super-16g-oc.html",
        "https://www.chillblast.com/asus-tuf-gaming-radeon-rx-7900-xtx-24g-oc.html",
        "https://www.chillblast.com/asus-dual-radeon-rx-7800-xt-16gb-oc.html",
    ],
    "storage": [
        "https://www.chillblast.com/samsung-990-pro-1tb-m-2-nvme-pcie-4-0-ssd-89.html",
        "https://www.chillblast.com/corsair-mp600-pro-xt-gen4-2tb-nvme-m-2-ssd-23.html",
        "https://www.chillblast.com/samsung-870-evo-1tb-sata-ssd-39.html",
        "https://www.chillblast.com/seagate-barracuda-2tb-7200rpm-256mb-39.html",
    ],
    "power_supply": [
        "https://www.chillblast.com/corsair-rm750e-750w-80-plus-gold-fully-modular-psu-black-uk.html",
        "https://www.chillblast.com/corsair-rm1000x-1000w-80-plus-gold-fully-modular-psu-black-uk-cable-35.html",
        "https://www.chillblast.com/corsair-rm1200x-1200w-80-plus-gold-fully-modular-psu-black-uk-cable-15.html",
    ],
    "case": [
        "https://www.chillblast.com/fractal-design-north-white-solid-tg-midi-tower-gaming-case-5.html",
        "https://www.chillblast.com/corsair-5000d-rgb-airflow-gaming-case-61.html",
        "https://www.chillblast.com/fractal-design-meshify-2-rgb-lite-black-tg-light-tint-2.html",
        "https://www.chillblast.com/lian-li-o11-dynamic-evo-white-01.html",
    ],
    "cooling": [
        "https://www.chillblast.com/corsair-icue-h150i-rgb-elite-liquid-cpu-cooler-white-80.html",
        "https://www.chillblast.com/arctic-freezer-i35-a-rgb-cpu-air-cooler-argb-13.html",
        "https://www.chillblast.com/noctua-nh-d15-chromax-black-cpu-cooler.html",
        "https://www.chillblast.com/deepcool-ag620-6-heatpipe-air-cooler-argb-w-controller-2.html",
    ]
}

# Output directory
IMAGES_DIR = os.path.join("static", "images", "components")

def ensure_dirs():
    """Create necessary directories if they don't exist."""
    for category in COMPONENT_PAGES.keys():
        category_dir = os.path.join(IMAGES_DIR, category)
        os.makedirs(category_dir, exist_ok=True)
    print("Directories created.")

def get_html_content(url):
    """Fetch HTML content from URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def extract_product_images(url, category, index):
    """Extract product images from a component page."""
    html_content = get_html_content(url)
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Product name for image naming
    product_name_elem = soup.select_one('h1.page-title span')
    if product_name_elem:
        product_name = product_name_elem.text.strip()
        product_name = slugify(product_name)
    else:
        product_name = f"{category}_{index}"
    
    # Find all product gallery images
    images = []
    
    # Try to get the main product image first (usually best quality)
    main_image = soup.select_one('img.gallery-placeholder__image')
    if main_image and 'src' in main_image.attrs:
        images.append(main_image['src'])
    
    # Get gallery images too
    gallery_images = soup.select('img.fotorama__img')
    for img in gallery_images:
        if 'src' in img.attrs and img['src'] not in images:
            images.append(img['src'])
    
    # Fallback to product thumbs if no gallery images found
    if not images:
        thumbs = soup.select('img.product-image-photo')
        for img in thumbs:
            if 'src' in img.attrs:
                images.append(img['src'])
    
    # Download images
    downloaded_paths = []
    for i, img_url in enumerate(images):
        if i >= 3:  # Limit to 3 images per product
            break
        
        filename = f"{product_name}_{i+1}.jpg" if i > 0 else f"{product_name}.jpg"
        filepath = download_image(img_url, category, filename)
        if filepath:
            downloaded_paths.append(filepath)
    
    return downloaded_paths

def download_image(url, category, filename):
    """Download image and save to images directory."""
    try:
        if not url.startswith('http'):
            url = urljoin(BASE_URL, url)
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        file_path = os.path.join(IMAGES_DIR, category, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded image: {category}/{filename}")
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

def main():
    """Main function to run the image downloader."""
    print("Starting component image download...")
    ensure_dirs()
    
    # Track results
    results = {}
    
    # Download images for each component type
    for category, urls in COMPONENT_PAGES.items():
        print(f"\nDownloading {category} images...")
        category_images = []
        
        for i, url in enumerate(urls):
            print(f"  Processing {url}")
            image_paths = extract_product_images(url, category, i)
            category_images.extend(image_paths)
            
            # Be nice to the server
            time.sleep(1)
        
        results[category] = len(category_images)
    
    # Print summary
    print("\nDownload summary:")
    for category, count in results.items():
        print(f"  {category.capitalize()}: {count} images")

if __name__ == "__main__":
    main()
