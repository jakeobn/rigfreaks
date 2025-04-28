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
        
        // Get the main content container
        this.content = document.querySelector('.page-content');
        
        // Set up event listeners for navigation
        this.setupEventListeners();
        
        // Show current page content with animation
        this.showContent();
        
        // Handle back button navigation
        window.addEventListener('popstate', () => {
            this.startTransition();
            setTimeout(() => {
                this.endTransition();
            }, 500);
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
        
        // Prevent default navigation
        event.preventDefault();
        
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
        
        // Get new content
        this.content = document.querySelector('.page-content');
        
        // Show new content with animation
        setTimeout(() => {
            this.showContent();
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
                // Parse the HTML
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                // Get the new content
                const newContent = doc.querySelector('.page-content').innerHTML;
                
                // Update the current content
                this.content.innerHTML = newContent;
                
                // Get the new page title
                const title = doc.querySelector('title').textContent;
                document.title = title;
                
                // End transition after a short delay
                setTimeout(() => {
                    this.endTransition();
                    
                    // Re-setup event listeners for the new content
                    this.setupEventListeners();
                    
                    // Reinitialize any scripts needed for the new page
                    this.reinitializeScripts();
                }, 100);
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
        // Reinitialize AOS
        if (typeof AOS !== 'undefined') {
            AOS.refresh();
        }
        
        // Re-run PC builder script if available
        if (typeof initPCBuilder === 'function') {
            initPCBuilder();
        }
        
        // Add more script reinitializations as needed
    }
}

// Initialize the transition controller
const pageTransitions = new PageTransitionController();

// Expose to global scope for debugging
window.pageTransitions = pageTransitions;