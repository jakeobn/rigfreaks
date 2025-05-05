// Home2.js - JavaScript for the home2 alternative template

document.addEventListener('DOMContentLoaded', function() {
    console.log('Home2 scripts initialized');
    
    // Initialize any animations or interactive elements
    initPerformanceCharts();
});

function initPerformanceCharts() {
    // Animation for performance bars
    const performanceBars = document.querySelectorAll('.performance-fill');
    performanceBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0';
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = width;
        }, 300);
    });
    
    // Animation for FPS bars
    const fpsBars = document.querySelectorAll('.fps-bar');
    fpsBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0';
        setTimeout(() => {
            bar.style.transition = 'width 1.2s ease-in-out';
            bar.style.width = width;
        }, 500);
    });
}
