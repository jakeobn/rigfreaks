/**
 * Load Components Script
 * Dynamically loads PC components from JSON data file
 */

document.addEventListener('DOMContentLoaded', () => {
    // Load component data from JSON file
    fetch('/static/data/components.json')
        .then(response => response.json())
        .then(data => {
            console.log('Component data loaded:', data);
            displayComponents(data);
        })
        .catch(error => {
            console.error('Error loading component data:', error);
        });
});

// Display components in their respective sections
function displayComponents(data) {
    // Get all step panels
    const stepPanels = document.querySelectorAll('.step-panel');
    
    // Process each panel
    stepPanels.forEach(panel => {
        const category = panel.getAttribute('data-category');
        
        // Skip panels without a category (like the review panel)
        if (!category || !data[category]) return;
        
        // Find the component cards container in this panel
        const cardsContainer = panel.querySelector('.component-cards');
        if (!cardsContainer) return;
        
        // Get components for this category
        const components = data[category];
        
        // Check if we have components to display
        if (components && components.length > 0) {
            // Clear the "no components" message if it exists
            const noComponentsMessage = cardsContainer.querySelector('.alert');
            if (noComponentsMessage) {
                cardsContainer.removeChild(noComponentsMessage);
            }
            
            // Create and append component cards
            components.forEach(component => {
                const card = createComponentCard(component, category);
                cardsContainer.appendChild(card);
                
                // Add event listener for selection
                card.addEventListener('click', () => {
                    // Find StepBuilder instance if it exists
                    if (window.stepBuilder) {
                        window.stepBuilder.selectComponent(card);
                    }
                });
                
                // Add event listener for details
                const detailsBtn = card.querySelector('.component-details-btn');
                if (detailsBtn) {
                    detailsBtn.addEventListener('click', (e) => {
                        e.stopPropagation(); // Prevent selecting the component
                        if (window.stepBuilder) {
                            window.stepBuilder.showComponentDetails(component.id);
                        }
                    });
                }
            });
            
            console.log(`Added ${components.length} ${category} components to the UI`);
        }
    });
}

// Create a component card element
function createComponentCard(component, category) {
    const card = document.createElement('div');
    card.className = 'component-card';
    card.setAttribute('data-component-id', component.id);
    card.setAttribute('data-price', component.price);
    
    // Add brand or other attributes for filtering
    if (component.brand) {
        card.setAttribute('data-brand', component.brand.toLowerCase());
    }
    
    // Add category-specific attributes
    switch(category) {
        case 'cpu':
            if (component.cores) card.setAttribute('data-cores', component.cores);
            break;
        case 'ram':
            if (component.capacity) card.setAttribute('data-capacity', component.capacity);
            break;
        case 'gpu':
            if (component.memory) card.setAttribute('data-memory', component.memory);
            break;
        case 'storage':
            if (component.capacity) card.setAttribute('data-capacity', component.capacity);
            if (component.type) card.setAttribute('data-type', component.type);
            break;
        case 'power_supply':
            if (component.wattage) card.setAttribute('data-wattage', component.wattage);
            break;
    }
    
    // Set card content
    card.innerHTML = `
        <div class="component-check">
            <i class="fas fa-check"></i>
        </div>
        <div class="component-image">
            <i class="${getCategoryIcon(category)}"></i>
        </div>
        <div class="component-name">${component.name}</div>
        <div class="component-specs">${component.description || ''}</div>
        <div class="component-price">£${component.price.toFixed(2)}</div>
        <button class="btn btn-sm btn-outline-light mt-2 component-details-btn">
            <i class="fas fa-info-circle me-1"></i> View Details
        </button>
    `;
    
    return card;
}

// Get appropriate icon for different component categories
function getCategoryIcon(category) {
    switch(category) {
        case 'case': return 'fas fa-desktop';
        case 'cpu': return 'fas fa-microchip';
        case 'motherboard': return 'fas fa-microchip';
        case 'ram': return 'fas fa-memory';
        case 'gpu': return 'fas fa-tv';
        case 'power_supply': return 'fas fa-bolt';
        case 'storage': return 'fas fa-hdd';
        case 'cooling': return 'fas fa-fan';
        default: return 'fas fa-cog';
    }
}