document.addEventListener('DOMContentLoaded', function() {
    const configFilters = document.querySelectorAll('.config-filter');
    const configCards = document.querySelectorAll('.config-card');
    
    // Filter functionality
    configFilters.forEach(filter => {
        filter.addEventListener('click', function() {
            // Remove active class from all filters
            configFilters.forEach(f => f.classList.remove('active'));
            
            // Add active class to clicked filter
            this.classList.add('active');
            
            const filterValue = this.getAttribute('data-filter');
            
            // Filter the cards
            configCards.forEach(card => {
                if (filterValue === 'all') {
                    card.style.display = 'block';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100);
                } else if (card.classList.contains(filterValue)) {
                    card.style.display = 'block';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
    
    // Animate performance gauges on scroll
    const performanceGauges = document.querySelectorAll('.perf-fill');
    
    // Initialize performance gauges at 0%
    performanceGauges.forEach(gauge => {
        gauge.style.width = '0%';
    });
    
    // Set up Intersection Observer to animate gauges when they come into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const gauge = entry.target;
                const finalWidth = gauge.getAttribute('style').split('width:')[1].trim().split('%')[0];
                
                // Reset width to 0 first
                gauge.style.width = '0%';
                
                // Animate to final width
                setTimeout(() => {
                    gauge.style.width = finalWidth + '%';
                }, 100);
                
                // Unobserve after animation
                observer.unobserve(gauge);
            }
        });
    }, {
        threshold: 0.2
    });
    
    // Observe all gauges
    performanceGauges.forEach(gauge => {
        observer.observe(gauge);
    });
});