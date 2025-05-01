/**
 * Step-by-Step PC Builder Script
 * Provides interactive functionality for a guided PC building experience
 */

// Main StepBuilder class to manage the build process
class StepBuilder {
    constructor() {
        // Initialize configuration
        this.currentStep = 0;
        this.totalSteps = 0;
        this.steps = [];
        this.buildConfig = {};
        this.totalPrice = 0;
        this.isOpeningDetails = false; // Flag to track popup open state
        
        // DOM elements
        this.stepContainer = null;
        this.progressBar = null;
        this.progressFill = null;
        this.stepIndicators = [];
        this.stepPanels = [];
        this.nextBtn = null;
        this.prevBtn = null;
        this.detailsPanel = null;
        
        // Bind methods to preserve 'this' context
        this.init = this.init.bind(this);
        this.setupEventListeners = this.setupEventListeners.bind(this);
        
        // Make this instance available globally for other scripts to use
        window.stepBuilder = this;
        this.goToStep = this.goToStep.bind(this);
        this.updateStepIndicators = this.updateStepIndicators.bind(this);
        this.selectComponent = this.selectComponent.bind(this);
        this.updateBuildSummary = this.updateBuildSummary.bind(this);
        this.showComponentDetails = this.showComponentDetails.bind(this);
        this.closeComponentDetails = this.closeComponentDetails.bind(this);
        this.validateStep = this.validateStep.bind(this);
        this.updateTotalPrice = this.updateTotalPrice.bind(this);
        this.submitBuild = this.submitBuild.bind(this);
        
        // Initialize event handler references
        this.handleEscapeKey = null;
        this.handleOutsideClick = null;
        
        // Initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', this.init);
    }
    
    // Initialize the step builder
    init() {
        console.log('Initializing Step Builder...');
        
        // Get main containers
        this.stepContainer = document.querySelector('.step-builder-container');
        if (!this.stepContainer) {
            console.warn('Step builder container not found');
            return;
        }
        
        // Get progress elements
        this.progressBar = document.querySelector('.step-progress-bar');
        this.progressFill = document.querySelector('.step-progress-fill');
        this.stepIndicators = document.querySelectorAll('.step-indicator');
        this.stepPanels = document.querySelectorAll('.step-panel');
        
        // Set total steps - we have exactly 10 steps (added OS), hardcode if needed
        this.totalSteps = 10;
        if (this.stepPanels.length != 10) {
            console.warn(`Expected 10 step panels, found ${this.stepPanels.length}`);
        }
        
        // Load components for the initial active step
        const activePanel = document.querySelector('.step-panel.active');
        if (activePanel) {
            const componentType = activePanel.getAttribute('data-category');
            if (componentType) {
                this.loadComponentsForStep(componentType);
            }
        }
        
        // Store steps configuration, guarantee 10 steps
        this.steps = [
            {
                index: 0,
                id: 'step-case',
                title: 'Choose Your Case',
                required: true,
                category: 'case'
            },
            {
                index: 1,
                id: 'step-cpu',
                title: 'Select Your Processor (CPU)',
                required: true,
                category: 'cpu'
            },
            {
                index: 2,
                id: 'step-motherboard',
                title: 'Select Your Motherboard',
                required: true,
                category: 'motherboard'
            },
            {
                index: 3,
                id: 'step-cooling',
                title: 'Select Your CPU Cooler',
                required: true,
                category: 'cooling'
            },
            {
                index: 4,
                id: 'step-ram',
                title: 'Select Your Memory (RAM)',
                required: true,
                category: 'ram'
            },
            {
                index: 5,
                id: 'step-gpu',
                title: 'Select Your Graphics Card',
                required: true,
                category: 'gpu'
            },
            {
                index: 6,
                id: 'step-power',
                title: 'Select Your Power Supply',
                required: true,
                category: 'power_supply'
            },
            {
                index: 7,
                id: 'step-storage',
                title: 'Select Your Storage (HDD/SSD)',
                required: true,
                category: 'storage'
            },
            {
                index: 8,
                id: 'step-os',
                title: 'Select Your Operating System',
                required: true,
                category: 'os'
            },
            {
                index: 9,
                id: 'step-review',
                title: 'Review Your Build',
                required: false,
                category: null
            }
        ];
        
        // Set up navigation buttons
        this.nextBtn = document.querySelector('.step-btn-next');
        this.prevBtn = document.querySelector('.step-btn-prev');
        
        // Set up details panel
        this.detailsPanel = document.querySelector('.component-details-panel');
        
        // Initialize event listeners
        this.setupEventListeners();
        
        // Set initial step
        this.goToStep(0);
        
        // Initialize empty build configuration
        this.initBuildConfig();
        
        console.log('Step Builder initialized with', this.totalSteps, 'steps');
    }
    
    // Initialize the build configuration object
    initBuildConfig() {
        // Create categories based on step data-category
        this.steps.forEach(step => {
            if (step.category) {
                this.buildConfig[step.category] = {
                    id: null,
                    name: null,
                    price: 0
                };
            }
        });
        
        // Ensure all required component categories are included in the config
        const requiredCategories = ['case', 'cpu', 'motherboard', 'ram', 'gpu', 'storage', 'power_supply', 'cooling', 'os'];
        requiredCategories.forEach(category => {
            if (!this.buildConfig[category]) {
                this.buildConfig[category] = {
                    id: null,
                    name: null,
                    price: 0
                };
            }
        });
        
        console.log('Build config initialized:', this.buildConfig);
    }
    
    // Set up event listeners
    setupEventListeners() {
        // Next button
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => {
                if (this.validateStep(this.currentStep)) {
                    if (this.currentStep < this.totalSteps - 1) {
                        this.goToStep(this.currentStep + 1);
                    } else {
                        this.submitBuild();
                    }
                } else {
                    // Show validation message
                    this.showValidationError();
                }
            });
        }
        
        // Previous button
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => {
                if (this.currentStep > 0) {
                    this.goToStep(this.currentStep - 1);
                }
            });
        }
        
        // Step indicators - allow clicking directly on any step
        this.stepIndicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                // Allow going to any step
                this.goToStep(index);
            });
        });
        
        // Component selection
        const componentCards = document.querySelectorAll('.component-card');
        componentCards.forEach(card => {
            card.addEventListener('click', () => {
                this.selectComponent(card);
            });
        });
        
        // Component details
        const detailButtons = document.querySelectorAll('.component-details-btn');
        detailButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent selecting the component when viewing details
                const componentId = button.closest('.component-card').getAttribute('data-component-id');
                this.showComponentDetails(componentId);
            });
        });
        
        // Close component details panel
        const closeDetailBtn = document.querySelector('.component-details-close');
        if (closeDetailBtn && this.detailsPanel) {
            closeDetailBtn.addEventListener('click', () => {
                this.closeComponentDetails();
            });
        }
        
        // Select component from the details panel
        const selectComponentBtn = document.querySelector('.component-select-btn');
        if (selectComponentBtn && this.detailsPanel) {
            selectComponentBtn.addEventListener('click', () => {
                // Get component ID directly from the button
                const componentId = selectComponentBtn.getAttribute('data-component-id');
                if (!componentId) {
                    console.error('No component ID found on select button');
                    return;
                }
                
                // Find component card with this ID
                const currentPanel = this.stepPanels[this.currentStep];
                const componentCard = currentPanel.querySelector(`[data-component-id="${componentId}"]`);
                
                if (componentCard) {
                    // Select this component
                    this.selectComponent(componentCard);
                    // Close the details panel
                    this.closeComponentDetails();
                    console.log(`Selected component from details panel: ${componentId}`);
                } else {
                    console.error(`Component with ID ${componentId} not found in current panel`);
                }
            });
        }
        
        // Filter tags
        const filterTags = document.querySelectorAll('.filter-tag');
        filterTags.forEach(tag => {
            tag.addEventListener('click', () => {
                const filterGroup = tag.closest('.filter-options');
                const isMultiSelect = filterGroup.hasAttribute('data-multi-select');
                
                // Toggle active state
                if (isMultiSelect) {
                    tag.classList.toggle('active');
                } else {
                    // Remove active from all siblings
                    filterGroup.querySelectorAll('.filter-tag').forEach(t => {
                        t.classList.remove('active');
                    });
                    tag.classList.add('active');
                }
                
                // Apply filters
                this.applyFilters();
            });
        });
        
        // Reset filters
        const resetFilterBtn = document.querySelector('.reset-filters-btn');
        if (resetFilterBtn) {
            resetFilterBtn.addEventListener('click', () => {
                document.querySelectorAll('.filter-tag').forEach(tag => {
                    tag.classList.remove('active');
                });
                this.applyFilters();
            });
        }
    }
    
    // Navigate to a specific step
    goToStep(stepIndex) {
        // Validate step index
        if (stepIndex < 0 || stepIndex >= this.totalSteps) {
            console.error('Invalid step index:', stepIndex);
            return;
        }
        
        // Update current step
        this.currentStep = stepIndex;
        
        // Hide all panels and show the current one
        this.stepPanels.forEach((panel, index) => {
            panel.classList.remove('active');
            if (index === stepIndex) {
                panel.classList.add('active');
                
                // Add animation classes
                panel.classList.add('step-fade-in');
                setTimeout(() => {
                    panel.classList.remove('step-fade-in');
                }, 500);
                
                // Get component type from the active panel
                const componentType = panel.getAttribute('data-category');
                if (componentType) {
                    // Load components for this step
                    this.loadComponentsForStep(componentType);
                }
                
                // If this is the review step, update the missing components alert
                if (stepIndex === this.totalSteps - 1) {
                    this.updateMissingComponentsAlert();
                }
            }
        });
        
        // Update progress indicators - only highlight the indicators corresponding to actual steps
        this.updateStepIndicators();
        
        // Update progress fill based on the number of actual steps, not indicators
        if (this.progressFill) {
            const progress = ((stepIndex) / (this.totalSteps - 1)) * 100;
            this.progressFill.style.width = `${progress}%`;
        }
        
        // Show/hide prev button based on current step
        if (this.prevBtn) {
            this.prevBtn.style.visibility = stepIndex === 0 ? 'hidden' : 'visible';
        }
        
        // Update next button text for last step
        if (this.nextBtn) {
            if (stepIndex === this.totalSteps - 1) {
                this.nextBtn.textContent = 'Complete Build';
                this.nextBtn.innerHTML = '<span>Complete Build</span><i class="fas fa-check"></i>';
            } else {
                this.nextBtn.textContent = 'Next Step';
                this.nextBtn.innerHTML = '<span>Next Step</span><i class="fas fa-arrow-right"></i>';
            }
        }
        
        console.log('Navigated to step', stepIndex + 1);
    }
    
    // Update step indicators
    updateStepIndicators() {
        this.stepIndicators.forEach((indicator, index) => {
            // Remove all states
            indicator.classList.remove('active', 'completed');
            
            // Add appropriate state
            if (index === this.currentStep) {
                indicator.classList.add('active');
            } else if (index < this.currentStep) {
                indicator.classList.add('completed');
            }
        });
    }
    
    // Get the highest completed step
    getHighestCompletedStep() {
        let highest = -1;
        for (let i = 0; i < this.totalSteps; i++) {
            if (this.validateStep(i, false)) {
                highest = i;
            } else {
                break;
            }
        }
        return highest;
    }
    
    // Handle component selection
    selectComponent(componentCardOrId, componentPrice) {
        let componentId, componentName;
        
        // Check if we received a DOM element or an ID string
        if (typeof componentCardOrId === 'string') {
            // We received an ID and price directly
            componentId = componentCardOrId;
            
            // Try to find the component name from the card
            const card = document.querySelector(`.component-card[data-component-id="${componentId}"]`);
            componentName = card ? card.querySelector('.component-name').textContent : componentId;
        } else {
            // We received a DOM element
            const componentCard = componentCardOrId;
            componentId = componentCard.getAttribute('data-component-id');
            componentName = componentCard.querySelector('.component-name').textContent;
            componentPrice = parseFloat(
                componentCard.getAttribute('data-price') || 
                componentCard.querySelector('.component-price').textContent.replace('£', '').trim()
            );
        }
        
        // Get the current active step panel for the category
        const activePanel = document.querySelector('.step-panel.active');
        const category = activePanel.getAttribute('data-category');
        
        if (!category) {
            console.error('Active step panel has no data-category attribute');
            return;
        }
        
        // Find the component card element if we were passed an ID
        let componentCard;
        if (typeof componentCardOrId === 'string') {
            componentCard = document.querySelector(`.component-card[data-component-id="${componentCardOrId}"]`);
        } else {
            componentCard = componentCardOrId;
        }
        
        // Check if this component is already selected
        const isCurrentlySelected = this.buildConfig[category].id === componentId;
        
        // Remove selected class from all components
        const allComponentCards = document.querySelectorAll('.component-card');
        allComponentCards.forEach(card => {
            card.classList.remove('selected');
        });
        
        // If the component wasn't already selected, select it. Otherwise, unselect it.
        if (!isCurrentlySelected) {
            // Add selected class to this component
            if (componentCard) {
                componentCard.classList.add('selected');
            }
            
            // Update build configuration
            this.buildConfig[category] = {
                id: componentId,
                name: componentName,
                price: componentPrice
            };
            
            console.log('Selected component:', this.buildConfig[category]);
        } else {
            // If we're unselecting, reset the build config for this category
            this.buildConfig[category] = {
                id: null,
                name: null,
                price: 0
            };
            
            console.log('Unselected component for category:', category);
        }
        
        // Update build summary
        this.updateBuildSummary();
    }
    
    // Update the build summary
    updateBuildSummary() {
        const summaryContainer = document.querySelector('.build-summary-list');
        if (!summaryContainer) return;
        
        // Clear existing summary
        summaryContainer.innerHTML = '';
        
        // Add each component to the summary
        for (const category in this.buildConfig) {
            const component = this.buildConfig[category];
            
            if (component.id) {
                const summaryItem = document.createElement('li');
                summaryItem.className = 'build-summary-item';
                summaryItem.innerHTML = `
                    <div class="build-summary-component">
                        <div class="build-summary-category">${this.formatCategoryName(category)}</div>
                        <div class="build-summary-selection">${component.name}</div>
                    </div>
                    <div class="build-summary-price">£${component.price.toFixed(2)}</div>
                `;
                summaryContainer.appendChild(summaryItem);
            }
        }
        
        // Update total price
        this.updateTotalPrice();
        
        // Update missing components alert if we're on the review step
        if (this.currentStep === this.totalSteps - 1) {
            this.updateMissingComponentsAlert();
        }
    }
    
    // Update the missing components alert on the review page
    updateMissingComponentsAlert() {
        // Check each required component
        const missingComponents = [];
        const missingComponentSteps = [];
        
        for (let i = 0; i < this.totalSteps - 1; i++) {
            const s = this.steps[i];
            // Skip non-required steps or steps without a category
            if (!s.required || !s.category) continue;
            
            // Check if a component is selected for this category
            const isSelected = !!this.buildConfig[s.category]?.id;
            if (!isSelected) {
                missingComponents.push(this.formatCategoryName(s.category));
                missingComponentSteps.push(i); // Store the step index for linking
            }
        }
        
        // Show or hide the missing components alert
        const missingAlert = document.getElementById('missing-components-alert');
        const missingList = document.getElementById('missing-components-list');
        
        if (!missingAlert || !missingList) return;
        
        if (missingComponents.length > 0) {
            // Clear previous list
            missingList.innerHTML = '';
            
            // Add each missing component as a list item with a link
            missingComponents.forEach((component, index) => {
                const li = document.createElement('li');
                const stepLink = document.createElement('a');
                stepLink.href = '#';
                stepLink.textContent = component;
                stepLink.className = 'text-white font-weight-bold';
                stepLink.style.textDecoration = 'underline';
                
                // Add click event to navigate to that step
                const stepIndex = missingComponentSteps[index];
                stepLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.goToStep(stepIndex);
                });
                
                li.appendChild(stepLink);
                missingList.appendChild(li);
            });
            
            // Show the alert
            missingAlert.style.display = 'block';
        } else {
            // Hide the alert if all components are selected
            missingAlert.style.display = 'none';
        }
    }
    
    // Format category name for display
    formatCategoryName(category) {
        return category.replace(/_/g, ' ')
            .replace(/\b\w/g, c => c.toUpperCase());
    }
    
    // Load components for the specified step
    loadComponentsForStep(componentType) {
        console.log(`Loading components for ${componentType}...`);
        const componentCardsContainer = document.querySelector('.step-panel.active .component-cards');
        if (!componentCardsContainer) {
            console.warn('No component cards container found for active step');
            return;
        }
        
        // Load component data from JSON file
        fetch('/static/data/components.json')
            .then(response => response.json())
            .then(data => {
                // Check if components exist for this type
                if (data[componentType] && data[componentType].length > 0) {
                    // Clear existing component cards
                    componentCardsContainer.innerHTML = '';
                    
                    // Create component cards
                    data[componentType].forEach(component => {
                        // Create and add component description if not present
                        if (!component.description) {
                            switch(componentType) {
                                case 'case':
                                    component.description = `${component.form_factor || ''} with ${component.specs?.["Included Fans"] || 'cooling support'}`;
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
                        
                        // Create component card HTML
                        const card = document.createElement('div');
                        card.className = 'component-card';
                        card.dataset.componentId = component.id;
                        card.dataset.price = component.price;
                        card.dataset.brand = component.brand?.toLowerCase() || '';
                        
                        // Check if this component is already selected in the build config
                        if (this.buildConfig[componentType] && this.buildConfig[componentType].id === component.id) {
                            card.classList.add('selected');
                        }
                        
                        // HTML structure for the component card
                        card.innerHTML = `
                            <div class="component-check">
                                <i class="fas fa-check"></i>
                            </div>
                            <div class="component-image">
                                ${component.image_url ? 
                                    `<img src="${component.image_url}" alt="${component.name}" class="img-fluid component-img">` : 
                                    this.getIconForType(componentType)}
                            </div>
                            <div class="component-name">${component.name}</div>
                            <div class="component-price">£${component.price.toFixed(2)}</div>
                            <button class="btn btn-sm btn-outline-light mt-2 component-details-btn">
                                <i class="fas fa-info-circle me-1"></i> View Details
                            </button>
                        `;
                        
                        // Add the component card to the container
                        componentCardsContainer.appendChild(card);
                        
                        // Add click event to select this component
                        card.addEventListener('click', () => {
                            this.selectComponent(card);
                        });
                        
                        // Add click event for the details button
                        const detailsBtn = card.querySelector('.component-details-btn');
                        if (detailsBtn) {
                            detailsBtn.addEventListener('click', (e) => {
                                e.stopPropagation(); // Prevent triggering the card click
                                this.showComponentDetails(component.id);
                            });
                        }
                    });
                    
                    console.log(`Loaded ${data[componentType].length} ${componentType} components`);
                } else {
                    // No components found for this type
                    console.log(`No ${componentType} components found in data`);
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
            })
            .catch(error => {
                console.error('Error loading component data:', error);
                componentCardsContainer.innerHTML = `
                    <div class="error-state text-center py-5">
                        <div class="mb-3">
                            <i class="fas fa-times-circle fa-3x text-danger"></i>
                        </div>
                        <h5 class="mb-2">Error Loading Components</h5>
                        <p class="text-muted">There was a problem loading the component data. Please try refreshing the page.</p>
                    </div>
                `;
            });
    }
    
    // Get icon for component type
    getIconForType(type) {
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
    
    // Show component details panel
    showComponentDetails(componentId) {
        // Find component data
        const componentCard = document.querySelector(`[data-component-id="${componentId}"]`);
        if (!componentCard) {
            console.error('Component not found:', componentId);
            return;
        }
        
        // Get the current category from the step panel
        const currentPanel = document.querySelector('.step-panel.active');
        const category = currentPanel.getAttribute('data-category');
        
        if (!category) {
            console.error('Could not determine component category');
            return;
        }
        
        // Navigate to the component details page
        window.location.href = `/component/${category}/${componentId}`;
        
        // The code below is kept for backward compatibility with the popup approach
        // but we're now using a full page approach instead
        if (!this.detailsPanel) return;
        
        // Set flag to prevent immediate closing
        this.isOpeningDetails = true;
        
        // Get component details
        const name = componentCard.querySelector('.component-name').textContent;
        const price = componentCard.querySelector('.component-price').textContent;
        const specs = componentCard.querySelector('.component-specs')?.textContent || 'No specifications available';
        
        // Update details panel content
        const detailsTitle = this.detailsPanel.querySelector('.component-details-title');
        const detailsName = this.detailsPanel.querySelector('.component-details-name');
        const detailsPrice = this.detailsPanel.querySelector('.component-details-price');
        const detailsSpecs = this.detailsPanel.querySelector('.component-details-description');
        const selectBtn = this.detailsPanel.querySelector('.component-select-btn');
        
        if (detailsTitle) detailsTitle.textContent = 'Component Details';
        if (detailsName) detailsName.textContent = name;
        if (detailsPrice) detailsPrice.textContent = price;
        if (detailsSpecs) detailsSpecs.textContent = specs;
        if (selectBtn) selectBtn.setAttribute('data-component-id', componentId);
        
        // Remove any existing event handlers to avoid duplicates
        document.removeEventListener('keydown', this.handleEscapeKey);
        document.removeEventListener('click', this.handleOutsideClick);
        
        // Create bound event handlers so we can remove them later
        this.handleEscapeKey = (e) => {
            if (e.key === 'Escape' && this.detailsPanel.classList.contains('open')) {
                this.closeComponentDetails();
            }
        };
        
        this.handleOutsideClick = (e) => {
            // If it's the initial click that opened the popup, ignore it
            if (this.isOpeningDetails) {
                this.isOpeningDetails = false;
                return;
            }
            
            // Check if the click is outside the panel
            if (this.detailsPanel.classList.contains('open') && !this.detailsPanel.contains(e.target)) {
                this.closeComponentDetails();
            }
        };
        
        // Add new event listeners
        document.addEventListener('keydown', this.handleEscapeKey);
        document.addEventListener('click', this.handleOutsideClick);
        
        // Open the panel
        this.detailsPanel.classList.add('open');
        
        // Focus on the panel (for accessibility)
        setTimeout(() => {
            const closeBtn = this.detailsPanel.querySelector('.component-details-close');
            if (closeBtn) closeBtn.focus();
            
            // Reset flag after a short delay to allow first click to be ignored
            setTimeout(() => {
                this.isOpeningDetails = false;
            }, 100);
        }, 100);
    }
    
    // Close component details panel
    closeComponentDetails() {
        if (!this.detailsPanel) return;
        
        // Close the panel
        this.detailsPanel.classList.remove('open');
        
        // Remove event listeners
        document.removeEventListener('keydown', this.handleEscapeKey);
        document.removeEventListener('click', this.handleOutsideClick);
    }
    
    // Apply selected filters
    applyFilters() {
        // Simplified filtering approach focusing on brand filters for now
        const currentStepPanel = document.querySelector('.step-panel.active');
        if (!currentStepPanel) return;
        
        const filterOptions = currentStepPanel.querySelector('.filter-options[data-filter-type="brand"]');
        if (!filterOptions) return;
        
        // Find which filter tag is active (if any)
        const activeFilterTag = filterOptions.querySelector('.filter-tag.active');
        const filterValue = activeFilterTag ? activeFilterTag.getAttribute('data-filter-value') : 'all';
        
        console.log('Active filter:', filterValue);
        
        // Get all component cards in the current step
        const componentCards = currentStepPanel.querySelectorAll('.component-card');
        
        // Show/hide components based on filter
        componentCards.forEach(card => {
            // If "all" is selected, show everything
            if (filterValue === 'all') {
                card.style.display = 'block';
                return;
            }
            
            // Otherwise, filter by brand
            const cardBrand = card.getAttribute('data-brand')?.toLowerCase();
            if (cardBrand === filterValue) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // Validate current step
    validateStep(stepIndex, showError = true) {
        const step = this.steps[stepIndex];
        
        // For the review step (final step), check if all required steps have components selected
        if (stepIndex === this.totalSteps - 1) {
            // Check each required component
            const missingComponents = [];
            const missingComponentSteps = [];
            
            for (let i = 0; i < this.totalSteps - 1; i++) {
                const s = this.steps[i];
                // Skip non-required steps or steps without a category
                if (!s.required || !s.category) continue;
                
                // Check if a component is selected for this category
                const isSelected = !!this.buildConfig[s.category]?.id;
                if (!isSelected) {
                    missingComponents.push(this.formatCategoryName(s.category));
                    missingComponentSteps.push(i); // Store the step index for linking
                }
            }
            
            // Show or hide the missing components alert
            const missingAlert = document.getElementById('missing-components-alert');
            const missingList = document.getElementById('missing-components-list');
            
            if (missingComponents.length > 0) {
                // Clear previous list
                missingList.innerHTML = '';
                
                // Add each missing component as a list item with a link
                missingComponents.forEach((component, index) => {
                    const li = document.createElement('li');
                    const stepLink = document.createElement('a');
                    stepLink.href = '#';
                    stepLink.textContent = component;
                    stepLink.className = 'text-white font-weight-bold';
                    stepLink.style.textDecoration = 'underline';
                    
                    // Add click event to navigate to that step
                    const stepIndex = missingComponentSteps[index];
                    stepLink.addEventListener('click', (e) => {
                        e.preventDefault();
                        this.goToStep(stepIndex);
                    });
                    
                    li.appendChild(stepLink);
                    missingList.appendChild(li);
                });
                
                // Show the alert
                missingAlert.style.display = 'block';
                
                // Show error message as well if needed
                if (showError) {
                    const errorMsg = document.querySelector(`#${step.id} .step-error-message`);
                    if (errorMsg) {
                        errorMsg.textContent = `Please select all required components before completing your build.`;
                        errorMsg.style.display = 'block';
                        
                        // Hide after 5 seconds
                        setTimeout(() => {
                            errorMsg.style.display = 'none';
                        }, 5000);
                    }
                }
                
                return false;
            } else {
                // Hide the alert if all components are selected
                missingAlert.style.display = 'none';
            }
            
            return missingComponents.length === 0;
        }
        
        // If step is not required, it's always valid
        if (!step.required) return true;
        
        // If step has a category, check if a component is selected
        if (step.category && this.buildConfig[step.category]) {
            const isValid = !!this.buildConfig[step.category].id;
            
            if (!isValid && showError) {
                // Show error message
                const errorMsg = document.querySelector(`#${step.id} .step-error-message`);
                if (errorMsg) {
                    errorMsg.textContent = 'Please select a component to continue';
                    errorMsg.style.display = 'block';
                    
                    // Hide after 3 seconds
                    setTimeout(() => {
                        errorMsg.style.display = 'none';
                    }, 3000);
                }
            }
            
            return isValid;
        }
        
        // If no specific validation, step is valid
        return true;
    }
    
    // Show validation error for current step
    showValidationError() {
        const currentPanel = this.stepPanels[this.currentStep];
        const errorContainer = currentPanel.querySelector('.step-error-message');
        
        if (errorContainer) {
            errorContainer.textContent = 'Please complete this step before continuing';
            errorContainer.style.display = 'block';
            
            // Highlight required components
            currentPanel.querySelectorAll('.component-card').forEach(card => {
                card.classList.add('required-highlight');
                
                // Remove highlight after animation
                setTimeout(() => {
                    card.classList.remove('required-highlight');
                }, 2000);
            });
            
            // Hide error after timeout
            setTimeout(() => {
                errorContainer.style.display = 'none';
            }, 3000);
        }
    }
    
    // Calculate and update total price
    updateTotalPrice() {
        // Calculate total from all selected components
        this.totalPrice = 0;
        for (const category in this.buildConfig) {
            if (this.buildConfig[category].id) {
                this.totalPrice += this.buildConfig[category].price;
            }
        }
        
        // Update total display
        const totalDisplay = document.querySelector('.build-total-price');
        if (totalDisplay) {
            totalDisplay.textContent = `£${this.totalPrice.toFixed(2)}`;
        }
    }
    
    // Submit final build
    submitBuild() {
        console.log('Submitting build:', this.buildConfig);
        
        // Show final success step if it exists
        const finalStep = document.querySelector('.final-step');
        if (finalStep) {
            // Hide all panels
            this.stepPanels.forEach(panel => {
                panel.classList.remove('active');
            });
            
            // Show final step
            finalStep.style.display = 'block';
            
            // Hide navigation buttons
            if (this.nextBtn) this.nextBtn.style.display = 'none';
            if (this.prevBtn) this.prevBtn.style.display = 'none';
        }
        
        // Create hidden form with build data and submit
        const formData = new FormData();
        
        // Add each component to form data
        for (const category in this.buildConfig) {
            if (this.buildConfig[category].id) {
                formData.append(`component_${category}`, this.buildConfig[category].id);
            }
        }
        
        // Add total price
        formData.append('total_price', this.totalPrice);
        
        // Submit form data via AJAX
        fetch('/add_to_cart', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Build submitted successfully:', data);
            
            // Redirect to cart if necessary
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        })
        .catch(error => {
            console.error('Error submitting build:', error);
        });
    }
}

// Initialize the step builder
const stepBuilder = new StepBuilder();

// Make available globally
window.stepBuilder = stepBuilder;