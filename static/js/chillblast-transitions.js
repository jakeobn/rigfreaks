/**
 * Chillblast-inspired Page Transitions
 * Adds smooth fade transitions between pages for a more polished user experience
 */

document.addEventListener('DOMContentLoaded', function() {
    // Apply fade-in effect when page loads
    document.body.classList.add('fade-in');
    
    // Handle all internal navigation links
    const internalLinks = document.querySelectorAll('a[href^="/"]:not([target]):not([download])');
    
    internalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Skip if ctrl/cmd/shift/middle-click (opens in new tab)
            if (e.ctrlKey || e.metaKey || e.shiftKey || e.which === 2) {
                return;
            }
            
            // Skip for links with specific classes that should bypass transition
            if (this.classList.contains('no-transition') || 
                this.parentNode.classList.contains('no-transition')) {
                return;
            }
            
            e.preventDefault();
            const targetHref = this.getAttribute('href');
            
            // Apply fade-out effect
            document.body.classList.remove('fade-in');
            document.body.classList.add('fade-out');
            
            // Navigate after transition completes
            setTimeout(function() {
                window.location.href = targetHref;
            }, 300); // Match this with CSS transition duration
        });
    });
    
    // Handle form submissions to apply transitions
    const forms = document.querySelectorAll('form:not(.no-transition)');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Don't apply transition for AJAX forms
            if (this.getAttribute('data-ajax') === 'true') {
                return;
            }
            
            // Skip for forms with specific classes
            if (this.classList.contains('no-transition')) {
                return;
            }
            
            document.body.classList.remove('fade-in');
            document.body.classList.add('fade-out');
            
            // Allow small delay for visual effect before actual submission
            // This will still submit the form normally
            setTimeout(() => {}, 200);
        });
    });
    
    // Handle browser back/forward buttons with History API
    window.addEventListener('popstate', function() {
        document.body.classList.remove('fade-in');
        document.body.classList.add('fade-out');
        
        setTimeout(function() {
            window.location.reload();
        }, 300);
    });
});