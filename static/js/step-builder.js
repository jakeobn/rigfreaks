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
        this.goToStep = this.goToStep.bind(this);
        this.updateStepIndicators = this.updateStepIndicators.bind(this);
        this.selectComponent = this.selectComponent.bind(this);
        this.updateBuildSummary = this.updateBuildSummary.bind(this);
        this.showComponentDetails = this.showComponentDetails.bind(this);
        this.validateStep = this.validateStep.bind(this);
        this.updateTotalPrice = this.updateTotalPrice.bind(this);
        this.submitBuild = this.submitBuild.bind(this);
        
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
        
        // Set total steps - we have exactly 8 steps, hardcode if needed
        this.totalSteps = 8;
        if (this.stepPanels.length != 8) {
            console.warn(`Expected 8 step panels, found ${this.stepPanels.length}`);
        }
        
        // Store steps configuration, guarantee 8 steps
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
                id: 'step-ram',
                title: 'Select Your Memory (RAM)',
                required: true,
                category: 'ram'
            },
            {
                index: 4,
                id: 'step-gpu',
                title: 'Select Your Graphics Card',
                required: true,
                category: 'gpu'
            },
            {
                index: 5,
                id: 'step-power',
                title: 'Select Your Power Supply',
                required: true,
                category: 'power_supply'
            },
            {
                index: 6,
                id: 'step-storage',
                title: 'Select Your Storage (HDD/SSD)',
                required: true,
                category: 'storage'
            },
            {
                index: 7,
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
        const requiredCategories = ['case', 'cpu', 'motherboard', 'ram', 'gpu', 'storage', 'power_supply', 'cooling'];
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
        
        // Step indicators - allow clicking directly on steps
        this.stepIndicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                // Only allow going to steps that are already completed or the next step
                if (index <= this.getHighestCompletedStep() + 1) {
                    this.goToStep(index);
                }
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
    selectComponent(componentCard) {
        const componentId = componentCard.getAttribute('data-component-id');
        const componentName = componentCard.querySelector('.component-name').textContent;
        const componentPrice = parseFloat(
            componentCard.getAttribute('data-price') || 
            componentCard.querySelector('.component-price').textContent.replace('$', '').trim()
        );
        const category = componentCard.closest('.step-panel').getAttribute('data-category');
        
        if (!category) {
            console.error('Component panel has no data-category attribute');
            return;
        }
        
        // Remove selected class from siblings
        const siblings = componentCard.closest('.component-cards').querySelectorAll('.component-card');
        siblings.forEach(card => {
            card.classList.remove('selected');
        });
        
        // Add selected class to this component
        componentCard.classList.add('selected');
        
        // Update build configuration
        this.buildConfig[category] = {
            id: componentId,
            name: componentName,
            price: componentPrice
        };
        
        // Update build summary
        this.updateBuildSummary();
        
        console.log('Selected component:', this.buildConfig[category]);
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
                    <div class="build-summary-price">$${component.price.toFixed(2)}</div>
                `;
                summaryContainer.appendChild(summaryItem);
            }
        }
        
        // Update total price
        this.updateTotalPrice();
    }
    
    // Format category name for display
    formatCategoryName(category) {
        return category.replace(/_/g, ' ')
            .replace(/\b\w/g, c => c.toUpperCase());
    }
    
    // Show component details panel
    showComponentDetails(componentId) {
        if (!this.detailsPanel) return;
        
        // Find component data
        const componentCard = document.querySelector(`[data-component-id="${componentId}"]`);
        if (!componentCard) {
            console.error('Component not found:', componentId);
            return;
        }
        
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
        
        // Create overlay if it doesn't exist
        let overlay = document.querySelector('.component-details-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'component-details-overlay';
            document.body.appendChild(overlay);
            
            // Add click event to close when clicking outside
            overlay.addEventListener('click', () => {
                this.closeComponentDetails();
            });
            
            // Add keyboard event for Escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.detailsPanel.classList.contains('open')) {
                    this.closeComponentDetails();
                }
            });
        }
        
        // Open the panel and show overlay
        this.detailsPanel.classList.add('open');
        overlay.classList.add('active');
        
        // Focus on the panel (for accessibility)
        setTimeout(() => {
            const closeBtn = this.detailsPanel.querySelector('.component-details-close');
            if (closeBtn) closeBtn.focus();
        }, 100);
        
        // Don't prevent all interactions, just make the modal the focus point
    }
    
    // Close component details panel
    closeComponentDetails() {
        if (!this.detailsPanel) return;
        
        // Close the panel and hide overlay
        this.detailsPanel.classList.remove('open');
        const overlay = document.querySelector('.component-details-overlay');
        if (overlay) overlay.classList.remove('active');
        
        // No need to restore body scrolling as we're not preventing it
    }
    
    // Apply selected filters
    applyFilters() {
        // Get all active filters by group
        const filterGroups = document.querySelectorAll('.filter-options');
        const activeFilters = {};
        
        filterGroups.forEach(group => {
            const filterType = group.getAttribute('data-filter-type');
            if (!filterType) return;
            
            activeFilters[filterType] = [];
            group.querySelectorAll('.filter-tag.active').forEach(tag => {
                activeFilters[filterType].push(tag.getAttribute('data-filter-value'));
            });
        });
        
        // Apply filters to components
        const allComponents = document.querySelectorAll('.component-card');
        allComponents.forEach(component => {
            let shouldShow = true;
            
            // Check each filter group
            for (const filterType in activeFilters) {
                // If no filters in this group, skip checking
                if (activeFilters[filterType].length === 0) continue;
                
                const componentValue = component.getAttribute(`data-${filterType}`);
                // If component doesn't match any selected filter in this group, hide it
                if (!activeFilters[filterType].includes(componentValue)) {
                    shouldShow = false;
                    break;
                }
            }
            
            // Show or hide based on filter match
            component.style.display = shouldShow ? 'block' : 'none';
        });
    }
    
    // Validate current step
    validateStep(stepIndex, showError = true) {
        const step = this.steps[stepIndex];
        
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
            totalDisplay.textContent = `$${this.totalPrice.toFixed(2)}`;
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