/**
 * Load Components Script
 * Dynamically loads PC components from JSON data file
 */

document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on a page that needs components loaded
    const componentCardsContainer = document.querySelector('.component-cards');
    if (!componentCardsContainer) {
        console.log('No component cards container found, skipping component loading');
        return;
    }

    // Get the current step from URL path or data attribute
    const stepElement = document.querySelector('[data-step]');
    if (!stepElement) {
        console.log('No step element found, skipping component loading');
        return;
    }

    const currentStep = parseInt(stepElement.dataset.step, 10);
    let componentType = 'case'; // Default to case step

    // Determine which component type to load based on step number
    switch (currentStep) {
        case 1: componentType = 'case'; break;
        case 2: componentType = 'cpu'; break;
        case 3: componentType = 'motherboard'; break;
        case 4: componentType = 'ram'; break;
        case 5: componentType = 'gpu'; break;
        case 6: componentType = 'power_supply'; break;
        case 7: componentType = 'storage'; break;
        default: console.log('Unknown or review step:', currentStep); return;
    }

    console.log(`Current step: ${currentStep}, loading ${componentType} components...`);

    // Load component data from JSON file
    fetch('/static/data/components.json')
        .then(response => response.json())
        .then(data => {
            console.log('Component data loaded:', data);
            if (data[componentType] && data[componentType].length > 0) {
                displayComponents(data, componentType);
            } else {
                console.log(`No ${componentType} components found in data`);
                displayEmptyState(componentType);
            }
        })
        .catch(error => {
            console.error('Error loading component data:', error);
            displayError();
        });
});

// Display components for the current step
function displayComponents(data, componentType) {
    const componentCardsContainer = document.querySelector('.component-cards');
    if (!componentCardsContainer) return;
    
    // Clear any existing cards
    componentCardsContainer.innerHTML = '';
    
    // Get components for the current type
    const components = data[componentType] || [];
    
    if (components.length === 0) {
        displayEmptyState(componentType);
        return;
    }
    
    // Create component cards
    components.forEach(component => {
        const card = createComponentCard(component, componentType);
        componentCardsContainer.appendChild(card);
    });
    
    // Add event listeners to the component cards
    setupComponentCardEvents();
}

// Create a component card element
function createComponentCard(component, type) {
    const card = document.createElement('div');
    card.className = 'component-card';
    card.dataset.componentId = component.id;
    card.dataset.price = component.price;
    card.dataset.brand = component.brand?.toLowerCase() || '';
    
    // HTML structure for the component card
    card.innerHTML = `
        <div class="component-check">
            <i class="fas fa-check"></i>
        </div>
        <div class="component-image">
            ${getIconForType(type)}
        </div>
        <div class="component-name">${component.name}</div>
        <div class="component-specs">${getComponentSpecs(component, type)}</div>
        <div class="component-price">£${component.price.toFixed(2)}</div>
        <button class="btn btn-sm btn-outline-light mt-2 component-details-btn">
            <i class="fas fa-info-circle me-1"></i> View Details
        </button>
    `;
    
    return card;
}

// Display empty state when no components are available
function displayEmptyState(componentType) {
    const componentCardsContainer = document.querySelector('.component-cards');
    if (!componentCardsContainer) return;
    
    componentCardsContainer.innerHTML = `
        <div class="empty-components-state text-center py-5">
            <div class="mb-3">
                <i class="fas fa-exclamation-circle fa-3x text-secondary"></i>
            </div>
            <h5 class="mb-2">No Components Available</h5>
            <p class="text-muted">No ${componentType.replace('_', ' ')} components are currently available.</p>
        </div>
    `;
}

// Display error message when component loading fails
function displayError() {
    const componentCardsContainer = document.querySelector('.component-cards');
    if (!componentCardsContainer) return;
    
    componentCardsContainer.innerHTML = `
        <div class="error-state text-center py-5">
            <div class="mb-3">
                <i class="fas fa-times-circle fa-3x text-danger"></i>
            </div>
            <h5 class="mb-2">Error Loading Components</h5>
            <p class="text-muted">There was a problem loading the component data. Please try refreshing the page.</p>
        </div>
    `;
}

// Get icon for component type
function getIconForType(type) {
    switch(type) {
        case 'cpu': return '<i class="fas fa-microchip"></i>';
        case 'motherboard': return '<i class="fas fa-server"></i>';
        case 'ram': return '<i class="fas fa-memory"></i>';
        case 'gpu': return '<i class="fas fa-film"></i>';
        case 'storage': return '<i class="fas fa-hdd"></i>';
        case 'power_supply': return '<i class="fas fa-plug"></i>';
        case 'case': return '<i class="fas fa-desktop"></i>';
        case 'cooling': return '<i class="fas fa-fan"></i>';
        default: return '<i class="fas fa-puzzle-piece"></i>';
    }
}

// Generate specs summary based on component type
function getComponentSpecs(component, type) {
    switch(type) {
        case 'cpu':
            return `${component.cores || ''} cores, ${component.base_clock || ''} GHz`;
        case 'motherboard':
            return `${component.socket || ''}, ${component.chipset || ''} chipset`;
        case 'ram':
            return `${component.capacity || ''} GB, ${component.speed || ''} MHz`;
        case 'gpu':
            return `${component.memory || ''} GB, ${component.memory_type || ''}`;
        case 'storage':
            return `${component.capacity || ''} ${component.type || 'SSD'}`;
        case 'power_supply':
            return `${component.wattage || ''} Watts, ${component.certification || ''}`;
        case 'case':
            return `${component.form_factor || ''} with ${component.specs?.["Included Fans"] || 'fans'}`;
        case 'cooling':
            return `${component.type || ''} cooling`;
        default:
            return component.description || '';
    }
}

// Setup event listeners for component cards
function setupComponentCardEvents() {
    // Add click events to component cards
    document.querySelectorAll('.component-card').forEach(card => {
        card.addEventListener('click', function() {
            // Remove selected class from all cards
            document.querySelectorAll('.component-card').forEach(c => {
                c.classList.remove('selected');
            });
            
            // Add selected class to clicked card
            this.classList.add('selected');
            
            // If we have a stepBuilder object (from step-builder.js), use it to update the selection
            if (window.stepBuilder) {
                window.stepBuilder.selectComponent(this.dataset.componentId, parseFloat(this.dataset.price));
            }
        });
        
        // Add click events to detail buttons
        const detailBtn = card.querySelector('.component-details-btn');
        if (detailBtn) {
            detailBtn.addEventListener('click', function(e) {
                e.stopPropagation(); // Prevent triggering card click
                
                const componentId = card.dataset.componentId;
                const currentStep = document.querySelector('[data-step]')?.dataset.step;
                let componentType = 'case';
                
                // Map step number to component type
                switch (parseInt(currentStep, 10)) {
                    case 1: componentType = 'case'; break;
                    case 2: componentType = 'cpu'; break;
                    case 3: componentType = 'motherboard'; break;
                    case 4: componentType = 'ram'; break;
                    case 5: componentType = 'gpu'; break;
                    case 6: componentType = 'power_supply'; break;
                    case 7: componentType = 'storage'; break;
                }
                
                // Navigate to component detail page
                window.location.href = `/component/${componentType}/${componentId}`;
            });
        }
    });
}
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