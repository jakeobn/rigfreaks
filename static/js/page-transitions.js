/**
 * Page Transitions Script
 * Handles smooth transitions between pages
 */
document.addEventListener('DOMContentLoaded', function() {
    const transitionOverlay = document.querySelector('.page-transition-overlay');
    const pageContent = document.querySelector('.page-content');
    const links = document.querySelectorAll('a[href]:not([href^="#"]):not([target]):not([href^="javascript:"]):not([href^="mailto:"]):not([href^="tel:"])');
    
    // Make sure the page is visible on initial load
    setTimeout(() => {
        pageContent.classList.add('visible');
    }, 100);
    
    // Add click event listeners to all internal links
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            // Skip transition for external links or special cases
            if (link.getAttribute('href').indexOf(window.location.hostname) === -1 && 
                link.getAttribute('href').indexOf('://') !== -1 ||
                link.getAttribute('href').startsWith('javascript:') ||
                link.getAttribute('href').startsWith('#') ||
                link.hasAttribute('target') ||
                link.classList.contains('no-transition') ||
                e.ctrlKey || e.metaKey) {
                return; // Allow default behavior
            }
            
            e.preventDefault();
            const targetUrl = link.getAttribute('href');
            
            // Start transition out
            pageContent.classList.remove('visible');
            transitionOverlay.classList.add('active');
            
            // Navigate to the new page after a brief delay
            setTimeout(() => {
                window.location.href = targetUrl;
            }, 300);
        });
    });
    
    // Handle back/forward browser navigation
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            // Page was loaded from browser cache (back/forward)
            pageContent.classList.add('visible');
            transitionOverlay.classList.remove('active');
        }
    });
});
