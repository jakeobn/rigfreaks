/**
 * Simple Page Transitions Script
 * Adds loading spinner during page loads without using AJAX
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing page transitions...');
    
    // Get overlay element
    const overlay = document.querySelector('.page-transition-overlay');
    const spinner = document.querySelector('.transition-loader');
    
    if (!overlay || !spinner) {
        console.error('Page transition elements not found');
        return;
    }
    
    // Add click listener to all internal links
    const links = document.querySelectorAll('a:not([target="_blank"]):not([href^="#"]):not([href^="javascript:"]):not([href^="mailto:"]):not([href^="tel:"])');
    
    links.forEach(link => {
        // Skip external links
        if (link.hostname !== window.location.hostname || link.hasAttribute('data-no-transition')) {
            return;
        }
        
        // For styling purposes
        link.classList.add('transition-link');
        
        // Add click event
        link.addEventListener('click', function(e) {
            // Don't transition if modifier keys are pressed
            if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) {
                return;
            }
            
            // Skip transition if we're in a form
            if (link.closest('form') !== null) {
                return;
            }
            
            // Get the URL
            const url = link.href;
            
            // Always use standard navigation for complex pages
            if (url.includes('/builder/') || 
                url.includes('/component/') || 
                url.includes('/add/') || 
                url.includes('/remove/')) {
                return; // Let browser handle it normally
            }
            
            // Prevent the default navigation
            e.preventDefault();
            
            // Show the overlay and spinner
            overlay.classList.add('active');
            spinner.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            // Navigate to the page after a short delay
            setTimeout(() => {
                window.location.href = url;
            }, 100);
        });
    });
    
    // Handle back/forward navigation
    window.addEventListener('pageshow', function(event) {
        if (overlay && overlay.classList.contains('active')) {
            overlay.classList.remove('active');
            if (spinner) spinner.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
    
    // Show content with animation if it exists
    const content = document.querySelector('.page-content') || 
                   document.querySelector('main') || 
                   document.querySelector('.container');
    
    if (content) {
        // Add the visible class after a short delay
        setTimeout(() => {
            content.classList.add('visible');
        }, 50);
    }
});

// When the page is being unloaded (navigating away)
window.addEventListener('beforeunload', function() {
    const overlay = document.querySelector('.page-transition-overlay');
    const spinner = document.querySelector('.transition-loader');
    
    if (overlay && spinner) {
        // Show the overlay and spinner
        overlay.classList.add('active');
        spinner.classList.add('active');
    }
});
