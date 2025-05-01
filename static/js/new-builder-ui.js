/**
 * Enhanced PC Builder UI handling
 * Integrates with the existing step-builder.js to provide a more interactive experience
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const summarySection = document.getElementById('collapseSummary');
    const summaryBtn = document.querySelector('.toggle-summary-button');
    const continueBtn = document.getElementById('continue-button');
    const summaryComponentsList = document.getElementById('summary-components-list');
    const summaryTotalPrice = document.getElementById('summary-total-price');
    const missingItemsCount = document.getElementById('missing-items-count');
    const expertModeSwitch = document.getElementById('expertModeSwitch');
    
    // Integrate with the step builder
    if (window.stepBuilder) {
        // Override the update build summary function to update our new summary panel
        const originalUpdateBuildSummary = window.stepBuilder.updateBuildSummary;
        window.stepBuilder.updateBuildSummary = function() {
            // Call the original method
            originalUpdateBuildSummary.call(window.stepBuilder);
            
            // Update our new summary panel
            updateOrderSummary();
        };
        
        // Set event handler for continue button
        if (continueBtn) {
            continueBtn.addEventListener('click', function() {
                // Find the first incomplete step
                for (let i = 0; i < window.stepBuilder.totalSteps; i++) {
                    if (!window.stepBuilder.validateStep(i, false)) {
                        window.stepBuilder.goToStep(i);
                        break;
                    }
                }
            });
        }
    }
    
    // Toggle summary section
    if (summaryBtn) {
        summaryBtn.addEventListener('click', function() {
            const isVisible = summarySection.classList.contains('show');
            if (isVisible) {
                summaryBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
            } else {
                summaryBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
            }
        });
    }
    
    // Expert mode toggle
    if (expertModeSwitch) {
        expertModeSwitch.addEventListener('change', function() {
            document.body.classList.toggle('expert-mode', this.checked);
            
            // In a real implementation, you would show/hide advanced options
            if (this.checked) {
                console.log('Expert mode enabled');
                // Show advanced options
            } else {
                console.log('Expert mode disabled');
                // Hide advanced options
            }
        });
    }
    
    // Update order summary based on current build config
    function updateOrderSummary() {
        if (!window.stepBuilder || !summaryComponentsList) return;
        
        // Clear existing items
        summaryComponentsList.innerHTML = '';
        
        // Create items for each component category
        const categories = [
            {type: 'case', label: 'Case'},
            {type: 'cpu', label: 'CPU'},
            {type: 'motherboard', label: 'Motherboard'},
            {type: 'cooling', label: 'CPU Cooler'},
            {type: 'ram', label: 'Memory'},
            {type: 'gpu', label: 'Graphics'},
            {type: 'power_supply', label: 'Power Supply'},
            {type: 'storage', label: 'Storage'},
            {type: 'os', label: 'Operating System'}
        ];
        
        let missingCount = 0;
        categories.forEach(category => {
            const component = window.stepBuilder.buildConfig[category.type];
            const isRequired = category.type !== 'os'; // All are required except OS
            const isSelected = component && component.id !== null;
            
            // Create the item element
            const item = document.createElement('div');
            item.className = 'main-order-summary-text text-start d-flex w-100 text-casing fw-semibold border-bottom border-silver-2 py-2';
            
            // Create the category name
            const nameSpan = document.createElement('span');
            nameSpan.className = 'summary-category-name-text pe-2 pe-sm-3';
            nameSpan.textContent = category.label;
            
            // Create the component info or not selected message
            const infoSpan = document.createElement('span');
            infoSpan.className = 'ms-auto text-end';
            
            if (isSelected) {
                infoSpan.className += ' text-black';
                infoSpan.innerHTML = `${component.name}<br><span class="text-success">£${component.price.toFixed(2)}</span>`;
            } else if (isRequired) {
                infoSpan.className += ' text-danger';
                infoSpan.textContent = 'Not selected - required!';
                missingCount++;
            } else {
                infoSpan.className += ' text-muted';
                infoSpan.textContent = 'Not selected';
            }
            
            // Add the elements to the item
            item.appendChild(nameSpan);
            item.appendChild(infoSpan);
            
            // Make the row clickable to navigate to that step
            item.style.cursor = 'pointer';
            item.addEventListener('click', function() {
                const stepIndex = window.stepBuilder.getStepIndexForCategory(category.type);
                if (stepIndex !== -1) {
                    window.stepBuilder.goToStep(stepIndex);
                }
            });
            
            // Add the item to the summary
            summaryComponentsList.appendChild(item);
        });
        
        // Update the total price
        if (summaryTotalPrice) {
            const total = window.stepBuilder.calculateTotalPrice();
            summaryTotalPrice.textContent = `£${total.toFixed(2)}`;
        }
        
        // Update missing items count
        if (missingItemsCount) {
            if (missingCount > 0) {
                missingItemsCount.textContent = `${missingCount} missing item${missingCount !== 1 ? 's' : ''}`;
                missingItemsCount.style.display = 'block';
            } else {
                missingItemsCount.style.display = 'none';
            }
        }
    }
    
    // Add a helper function to get step index by category
    if (window.stepBuilder) {
        window.stepBuilder.getStepIndexForCategory = function(category) {
            const steps = document.querySelectorAll('.step-panel');
            for (let i = 0; i < steps.length; i++) {
                if (steps[i].dataset.category === category) {
                    return parseInt(steps[i].dataset.step) - 1;
                }
            }
            return -1;
        };
    }
    
    // Initial update
    setTimeout(() => {
        updateOrderSummary();
    }, 500);
});
