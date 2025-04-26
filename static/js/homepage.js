document.addEventListener('DOMContentLoaded', function() {
    // Mouse move parallax effect for the hero image
    const heroCard = document.querySelector('.hero-3d-card');
    const heroImage = document.querySelector('.hero-image-modern');
    
    if (heroCard && heroImage) {
        // Enhanced parallax settings for the hero card
        VanillaTilt.init(heroCard, {
            max: 15,               // Maximum tilt rotation in degrees
            perspective: 1000,     // Transform perspective, the lower the more extreme the tilt gets
            scale: 1.05,           // 2 = 200%, 1.5 = 150%, etc.
            speed: 1000,           // Speed of the enter/exit transition
            glare: true,           // Whether to enable glare effect
            "max-glare": 0.1,      // The maximum "glare" opacity
            gyroscope: true,       // Boolean to enable/disable device orientation detection
            gyroscopeMinAngleX: -10, // This is the bottom limit of the device angle on X axis, meaning the tilt will stop at this value
            gyroscopeMaxAngleX: 10,  // This is the top limit of the device angle on X axis, meaning the tilt will stop at this value
            gyroscopeMinAngleY: -10, // This is the bottom limit of the device angle on Y axis, meaning the tilt will stop at this value
            gyroscopeMaxAngleY: 10   // This is the top limit of the device angle on Y axis, meaning the tilt will stop at this value
        });

        // Additional direct mouse parallax effect for the image itself
        heroCard.addEventListener('mousemove', function(e) {
            // Calculate mouse position relative to the card center
            const rect = heroCard.getBoundingClientRect();
            const x = e.clientX - rect.left; // X position within the element
            const y = e.clientY - rect.top;  // Y position within the element
            
            // Calculate the center of the card
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            // Calculate the distance from the center (-1 to 1)
            const moveX = (x - centerX) / centerX;
            const moveY = (y - centerY) / centerY;
            
            // Apply a slight movement to the image based on mouse position
            // The multiplier determines the strength of the effect
            const multiplier = 30; // Adjust for more/less movement
            heroImage.style.transform = `translate3d(${moveX * multiplier}px, ${moveY * multiplier}px, 0)`;
        });

        // Reset position when mouse leaves the card
        heroCard.addEventListener('mouseleave', function() {
            heroImage.style.transform = 'translate3d(0, 0, 0)';
        });
    }
});