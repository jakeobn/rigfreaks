/**
 * Component Gallery Initialization
 * Handles image gallery functionality for component detail pages
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all gallery links and set up click events
    const galleryLinks = document.querySelectorAll('.component-gallery-item');
    
    if (galleryLinks.length > 0) {
        galleryLinks.forEach(function(link) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Collect all gallery items for this component
                const galleryItems = document.querySelectorAll('.component-gallery-item');
                const links = Array.from(galleryItems).map(item => ({
                    href: item.href,
                    title: item.getAttribute('data-title') || item.querySelector('img').alt
                }));
                
                // Find the index of the clicked item
                const index = Array.from(galleryItems).indexOf(this);
                
                // Initialize the blueimp Gallery
                blueimp.Gallery(links, {
                    index: index,
                    event: e,
                    onslide: function(index, slide) {
                        // Custom slide event handling if needed
                    },
                    onclosed: function() {
                        // Custom close event handling if needed
                    }
                });
            });
        });
    }
    
    // Add hover effect to main component image
    const mainComponentImage = document.querySelector('.component-image');
    if (mainComponentImage) {
        const componentImg = mainComponentImage.querySelector('img');
        if (componentImg) {
            componentImg.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.05)';
                this.style.transition = 'transform 0.3s ease';
            });
            
            componentImg.addEventListener('mouseleave', function() {
                this.style.transform = '';
            });
        }
    }
});