"""Move and organize component images from attached_assets folder.

This script moves existing component images from the attached_assets directory 
into the appropriate component category folders for use in the PC builder.
"""

import os
import shutil
import re

# Source directory for images
SOURCE_DIR = "attached_assets"

# Output directory for component images
IMAGES_DIR = os.path.join("static", "images", "components")

# Component categories and their associated file patterns
COMPONENT_PATTERNS = {
    "cpu": [
        r".*Ryzen.*\.(jpg|png|webp)$",
        r".*Core.*i[579].*\.(jpg|png|webp)$",
        r".*processor.*\.(jpg|png|webp)$",
        r".*cpu.*\.(jpg|png|webp)$"
    ],
    "motherboard": [
        r".*ASUS.*\.(jpg|png|webp)$",
        r".*Gigabyte.*\.(jpg|png|webp)$",
        r".*motherboard.*\.(jpg|png|webp)$",
        r".*WIFI.*\.(jpg|png|webp)$",
        r".*Gaming.*\.(jpg|png|webp)$", 
        r".*-(Z|B)\d+.*\.(jpg|png|webp)$"
    ],
    "ram": [
        r".*RAM.*\.(jpg|png|webp)$",
        r".*memory.*\.(jpg|png|webp)$",
        r".*Kingston.*\.(jpg|png|webp)$",
        r".*Fury.*\.(jpg|png|webp)$",
        r".*Vengeance.*\.(jpg|png|webp)$",
        r".*DDR\d.*\.(jpg|png|webp)$"
    ],
    "gpu": [
        r".*rtx.*\.(jpg|png|webp)$",
        r".*nvidia.*\.(jpg|png|webp)$",
        r".*radeon.*\.(jpg|png|webp)$", 
        r".*graphics.*\.(jpg|png|webp)$"
    ],
    "storage": [
        r".*SSD.*\.(jpg|png|webp)$",
        r".*storage.*\.(jpg|png|webp)$",
        r".*Samsung.*\.(jpg|png|webp)$",
        r".*MZ-V.*\.(jpg|png|webp)$",
        r".*MP600.*\.(jpg|png|webp)$"
    ],
    "case": [
        r".*case.*\.(jpg|png|webp)$",
        r".*tower.*\.(jpg|png|webp)$",
        r".*chassis.*\.(jpg|png|webp)$"
    ],
    "cooling": [
        r".*cooler.*\.(jpg|png|webp)$", 
        r".*cooling.*\.(jpg|png|webp)$",
        r".*AK620.*\.(jpg|png|webp)$",
        r".*liquid.*\.(jpg|png|webp)$",
        r".*fan.*\.(jpg|png|webp)$"
    ],
    "power_supply": [
        r".*PSU.*\.(jpg|png|webp)$",
        r".*power.*\.(jpg|png|webp)$"
    ]
}

# Create the necessary directories
def ensure_dirs():
    """Create necessary component directories if they don't exist."""
    for category in COMPONENT_PATTERNS.keys():
        category_dir = os.path.join(IMAGES_DIR, category)
        os.makedirs(category_dir, exist_ok=True)
    print("Component directories created.")

# Function to check if a file matches any of the patterns for a category
def matches_category(filename, patterns):
    for pattern in patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            return True
    return False

# Copy component images to their respective directories
def organize_images():
    """Organize component images into their category folders."""
    ensure_dirs()
    
    # Track images found for each category
    found_images = {category: [] for category in COMPONENT_PATTERNS.keys()}
    
    # Get all files from source directory
    all_files = os.listdir(SOURCE_DIR)
    
    # Filter for image files (jpg, png, webp)
    image_files = [f for f in all_files if re.search(r'\.(jpg|png|webp)$', f, re.IGNORECASE)]
    
    # Process each image
    for image_file in image_files:
        source_path = os.path.join(SOURCE_DIR, image_file)
        
        # Find matching category
        for category, patterns in COMPONENT_PATTERNS.items():
            if matches_category(image_file, patterns):
                destination_path = os.path.join(IMAGES_DIR, category, image_file)
                shutil.copy2(source_path, destination_path)
                found_images[category].append(image_file)
                print(f"Copied {image_file} to {category} folder")
                break
    
    # Handle the "Untitled design" images which may contain various components
    # These are likely pre-made component images from design software
    untitled_designs = [f for f in all_files if "Untitled design" in f]
    
    # Distribute some of these images to categories that don't have enough
    for category, images in found_images.items():
        if len(images) < 3 and untitled_designs:  # Ensure each category has at least 3 images
            needed = 3 - len(images)
            for i in range(min(needed, len(untitled_designs))):
                image_file = untitled_designs.pop(0)  # Take from the beginning
                source_path = os.path.join(SOURCE_DIR, image_file)
                destination_path = os.path.join(IMAGES_DIR, category, image_file)
                shutil.copy2(source_path, destination_path)
                found_images[category].append(image_file)
                print(f"Supplemented {category} with {image_file}")
    
    # Print summary
    print("\nImage organization summary:")
    for category, images in found_images.items():
        print(f"  {category.capitalize()}: {len(images)} images")

def main():
    """Main function to run the image organizer."""
    print("Starting component image organization...")
    organize_images()
    print("Image organization complete!")

if __name__ == "__main__":
    main()
