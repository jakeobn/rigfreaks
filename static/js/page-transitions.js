/**
 * Page Transitions Script
 * Adds smooth transition effects between pages
 */

// Main transition controller
class PageTransitionController {
    constructor() {
        // Initialize properties
        this.overlay = null;
        this.loader = null;
        this.content = null;
        this.isTransitioning = false;
        this.transitionLinks = [];
        
        // Bind methods
        this.init = this.init.bind(this);
        this.createOverlay = this.createOverlay.bind(this);
        this.setupEventListeners = this.setupEventListeners.bind(this);
        this.handleLinkClick = this.handleLinkClick.bind(this);
        this.startTransition = this.startTransition.bind(this);
        this.endTransition = this.endTransition.bind(this);
        this.navigateToPage = this.navigateToPage.bind(this);
        this.showContent = this.showContent.bind(this);
        
        // Initialize on load
        window.addEventListener('load', this.init);
    }
    
    // Initialize the transition system
    init() {
        console.log('Initializing page transitions...');
        
        // Create overlay element if it doesn't exist
        this.createOverlay();
        
        // Get the main content container with fallbacks
        this.content = document.querySelector('.page-content') || 
                      document.querySelector('main') || 
                      document.querySelector('.container');
        
        // If still no content found, create a wrapper around the body content
        if (!this.content) {
            console.warn('No content container found, creating one');
            this.content = document.createElement('div');
            this.content.className = 'page-content';
            
            // Move all body children into this container except our overlay
            const bodyChildren = Array.from(document.body.children);
            bodyChildren.forEach(child => {
                if (child !== this.overlay && child.tagName !== 'SCRIPT') {
                    this.content.appendChild(child);
                }
            });
            
            // Add the content container to the body
            document.body.appendChild(this.content);
        }
        
        // Set up event listeners for navigation
        this.setupEventListeners();
        
        // Show current page content with animation
        this.showContent();
        
        // Handle back button navigation
        window.addEventListener('popstate', () => {
            this.startTransition();
            setTimeout(() => {
                // Force reload on back/forward to avoid issues
                window.location.reload();
            }, 300);
        });
    }
    
    // Create the transition overlay
    createOverlay() {
        // Check if overlay already exists
        if (document.querySelector('.page-transition-overlay')) {
            this.overlay = document.querySelector('.page-transition-overlay');
            this.loader = document.querySelector('.transition-loader');
            return;
        }
        
        // Create overlay element
        this.overlay = document.createElement('div');
        this.overlay.className = 'page-transition-overlay';
        
        // Create loader element
        this.loader = document.createElement('div');
        this.loader.className = 'transition-loader';
        
        // Create spinner element
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        
        // Append elements
        this.loader.appendChild(spinner);
        this.overlay.appendChild(this.loader);
        document.body.appendChild(this.overlay);
    }
    
    // Set up event listeners for navigation links
    setupEventListeners() {
        // Get all navigation links
        this.transitionLinks = document.querySelectorAll('a:not([target="_blank"]):not([href^="#"]):not([href^="javascript:"]):not([href^="mailto:"]):not([href^="tel:"])');
        
        // Add click event listener to each link
        this.transitionLinks.forEach(link => {
            // Skip external links or links that already have event listeners
            if (link.hostname !== window.location.hostname || link.hasAttribute('data-no-transition') || link.hasAttribute('data-transition-attached')) {
                return;
            }
            
            // Add class for styling
            link.classList.add('transition-link');
            
            // Mark as having the event listener attached
            link.setAttribute('data-transition-attached', 'true');
            
            // Add click event listener
            link.addEventListener('click', this.handleLinkClick);
        });
    }
    
    // Handle link click event
    handleLinkClick(event) {
        const link = event.currentTarget;
        const url = link.href;
        
        // Don't transition if modifier keys are pressed
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
            return;
        }
        
        // Skip transition if we're in a form or if skip transition data attribute is present
        const isInForm = link.closest('form') !== null;
        const skipTransition = link.hasAttribute('data-no-transition') || 
                              link.hasAttribute('data-skip-transition');
        
        if (isInForm || skipTransition) {
            return; // Let the browser handle the navigation normally
        }
        
        // Prevent default navigation
        event.preventDefault();
        
        // For step builder links, just use regular navigation to avoid script issues
        if (url.includes('/builder/step-by-step') || 
            url.includes('/builder/classic') || 
            url.includes('/add/') || 
            url.includes('/remove/')) {
            // Use normal navigation for these routes
            window.location.href = url;
            return;
        }
        
        // Start transition effect
        this.startTransition();
        
        // Navigate to the new page after a short delay
        setTimeout(() => {
            this.navigateToPage(url);
        }, 400);
    }
    
    // Start the transition effect
    startTransition() {
        if (this.isTransitioning) return;
        
        this.isTransitioning = true;
        
        // Fade out current content
        if (this.content) {
            this.content.style.opacity = '0';
            this.content.style.transform = 'translateY(20px)';
        }
        
        // Show overlay and loader
        this.overlay.classList.add('active');
        this.loader.classList.add('active');
        
        // Disable scrolling during transition
        document.body.style.overflow = 'hidden';
    }
    
    // End the transition effect
    endTransition() {
        // Hide overlay and loader
        this.overlay.classList.remove('active');
        this.loader.classList.remove('active');
        
        // Re-enable scrolling
        document.body.style.overflow = '';
        
        // Get new content with fallbacks
        this.content = document.querySelector('.page-content') || 
                      document.querySelector('main') || 
                      document.querySelector('.container');
        
        if (!this.content) {
            console.warn('No content container found after transition');
            // If we're in a bad state, just reload the page
            window.location.reload();
            return;
        }
        
        // Show new content with animation
        setTimeout(() => {
            if (this.content) {
                // Reset any transition styles
                this.content.style.opacity = '';
                this.content.style.transform = '';
                this.showContent();
            }
            this.isTransitioning = false;
        }, 100);
    }
    
    // Navigate to a new page
    navigateToPage(url) {
        // Use history API to change URL
        window.history.pushState({}, '', url);
        
        // Fetch the new page
        fetch(url)
            .then(response => response.text())
            .then(html => {
                try {
                    // Parse the HTML
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    
                    // Get the new content - use more flexible selectors
                    let newContentElement = doc.querySelector('.page-content');
                    
                    // Fallbacks if main selector not found
                    if (!newContentElement) {
                        newContentElement = doc.querySelector('main');
                    }
                    if (!newContentElement) {
                        newContentElement = doc.querySelector('.container');
                    }
                    
                    // If still not found, use the body content
                    if (!newContentElement) {
                        throw new Error('Could not find content container in the new page');
                    }
                    
                    const newContent = newContentElement.innerHTML;
                    
                    // Make sure we have a valid content container
                    if (!this.content) {
                        this.content = document.querySelector('.page-content') || 
                                      document.querySelector('main') || 
                                      document.querySelector('.container');
                        
                        if (!this.content) {
                            throw new Error('Could not find content container in current page');
                        }
                    }
                    
                    // Update the current content
                    this.content.innerHTML = newContent;
                    
                    // Get the new page title
                    const title = doc.querySelector('title');
                    if (title) {
                        document.title = title.textContent;
                    }
                    
                    // End transition after a short delay
                    setTimeout(() => {
                        this.endTransition();
                        
                        // Re-setup event listeners for the new content
                        this.setupEventListeners();
                        
                        // Reinitialize any scripts needed for the new page
                        this.reinitializeScripts();
                    }, 100);
                } catch (error) {
                    console.error('Error processing new page:', error);
                    // Fallback to traditional navigation on error
                    window.location.href = url;
                }
            })
            .catch(error => {
                console.error('Error during page transition:', error);
                // Fallback to traditional navigation on error
                window.location.href = url;
            });
    }
    
    // Show content with animation
    showContent() {
        if (this.content) {
            setTimeout(() => {
                this.content.classList.add('visible');
            }, 50);
        }
    }
    
    // Reinitialize scripts after page transition
    reinitializeScripts() {
        try {
            // Reinitialize AOS
            if (typeof AOS !== 'undefined') {
                AOS.refresh();
            }
            
            // Re-run PC builder script if available
            if (typeof initPCBuilder === 'function') {
                initPCBuilder();
            }
            
            // Re-initialize step builder if we're on that page
            if (window.location.pathname.includes('/builder/step-by-step')) {
                console.log("Reinitializing step builder...");
                // If the step builder class exists, construct a new instance
                if (typeof StepBuilder === 'function') {
                    window.stepBuilder = new StepBuilder();
                }
            }
            
            // Re-run specific scripts based on the current route/page
            const currentPath = window.location.pathname;
            
            // Run specific initializations based on the page we're on
            if (currentPath === '/' || currentPath.includes('/index')) {
                // Home page specific scripts
                console.log("Reinitializing homepage scripts");
            } else if (currentPath.includes('/builder/classic')) {
                // Classic builder page
                console.log("Reinitializing classic builder scripts");
            }
            
            // Execute any global scripts that should always run
            if (typeof window.initializeDropdowns === 'function') {
                window.initializeDropdowns();
            }
        } catch (error) {
            console.error("Error reinitializing scripts:", error);
        }
    }
}

// Initialize the transition controller
const pageTransitions = new PageTransitionController();

// Expose to global scope for debugging
window.pageTransitions = pageTransitions;