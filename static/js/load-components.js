/**
 * Load Components Script
 * Dynamically loads PC components from JSON data file
 *
 * NOTE: This script is now mostly superseded by the StepBuilder's loadComponentsForStep method
 * but is kept for compatibility with non-step-builder pages.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Check if StepBuilder is active - if so, it will handle component loading
    if (window.stepBuilder) {
        console.log('StepBuilder detected, component loading will be handled by StepBuilder');
        return;
    }
    
    // Check if we're on a page that needs components loaded
    const componentCardsContainer = document.querySelector('.component-cards');
    if (!componentCardsContainer) {
        console.log('No component cards container found, skipping component loading');
        return;
    }

    // Get the current step by finding the active step panel
    const activeStepPanel = document.querySelector('.step-panel.active');
    if (!activeStepPanel) {
        console.log('No active step panel found, skipping component loading');
        return;
    }

    // Get component type from the active panel's data-category attribute
    const componentType = activeStepPanel.getAttribute('data-category') || 'case';
    console.log(`Found active step panel with category: ${componentType}`);

    // We already have the component type from the active panel
    console.log(`Loading ${componentType} components...`);

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
        // Add a component specs description if not already present
        if (!component.description) {
            // Create a description based on specs
            switch(componentType) {
                case 'case':
                    component.description = `${component.form_factor} with ${component.specs?.["Included Fans"] || 'cooling support'}`;
                    break;
                case 'cpu':
                    component.description = `${component.cores || ''} cores, ${component.base_clock || ''} GHz`;
                    break;
                case 'motherboard':
                    component.description = `${component.socket || ''}, ${component.chipset || ''} chipset`;
                    break;
                case 'ram':
                    component.description = `${component.capacity || ''} GB, ${component.speed || ''} MHz`;
                    break;
                case 'gpu':
                    component.description = `${component.memory || ''} GB, ${component.memory_type || ''}`;
                    break;
                case 'storage':
                    component.description = `${component.capacity || ''} ${component.type || 'SSD'}`;
                    break;
                case 'power_supply':
                    component.description = `${component.wattage || ''} Watts, ${component.certification || ''}`;
                    break;
                default:
                    component.description = '';
            }
        }
        
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
            ${component.image_url ? 
                `<img src="${component.image_url}" alt="${component.name}" class="img-fluid component-img">` : 
                getIconForType(type)}
        </div>
        <div class="component-name">${component.name}</div>
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
                // Get the active step panel to determine the component type
                const activePanel = document.querySelector('.step-panel.active');
                const componentType = activePanel ? activePanel.getAttribute('data-category') : 'case';
                
                // Navigate to component detail page
                window.location.href = `/component/${componentType}/${componentId}`;
            });
        }
    });
}