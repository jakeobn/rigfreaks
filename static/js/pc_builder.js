document.addEventListener('DOMContentLoaded', function() {
    console.log('PC Builder script loaded');
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Skip component selection initialization since it's handled in builder.html
    // The script in the HTML already sets up event listeners for:
    // - componentSelectionContainer
    // - component-dropdown-btn elements
    // - closeComponentSelection button
    // - cancelComponentSelection button
    
    // Only initialize these elements if we need them
    const componentSearchDesktop = document.getElementById('componentSearchDesktop');
    const componentSearchMobile = document.getElementById('componentSearchMobile');
    const siteSearchInput = document.getElementById('siteSearchInput');
    const sortOptions = document.querySelectorAll('.sort-option') || [];
    let currentCategory = '';

    // Helper function to load components for a category
    function loadComponentsForCategory(category) {
        console.log('Loading components for category:', category);
        
        // Check if required elements exist
        const componentCardsWrapper = document.getElementById('componentCardsWrapper');
        if (!componentCardsWrapper) {
            console.error('Component cards wrapper not found');
            return;
        }
        
        const componentLoading = document.getElementById('component-loading');
        if (!componentLoading) {
            console.error('Component loading element not found');
            return;
        }
        
        const modalCategoryIcon = document.getElementById('modalCategoryIcon');
        const componentModalLabel = document.getElementById('componentModalLabel');
        const modalCategoryDescription = document.getElementById('modalCategoryDescription');
        
        if (!modalCategoryIcon || !componentModalLabel || !modalCategoryDescription) {
            console.error('One or more modal elements not found');
            return;
        }
        
        // Update modal title and description
        let categoryName = '';
        let categoryIcon = '';
        
        switch(category) {
            case 'cpu':
                categoryName = 'Processor';
                categoryIcon = '<i class="fas fa-microchip"></i>';
                break;
            case 'motherboard':
                categoryName = 'Motherboard';
                categoryIcon = '<i class="fas fa-server"></i>';
                break;
            case 'ram':
                categoryName = 'Memory';
                categoryIcon = '<i class="fas fa-memory"></i>';
                break;
            case 'gpu':
                categoryName = 'Graphics Card';
                categoryIcon = '<i class="fas fa-tv"></i>';
                break;
            case 'storage':
                categoryName = 'Storage';
                categoryIcon = '<i class="fas fa-hdd"></i>';
                break;
            case 'power_supply':
                categoryName = 'Power Supply';
                categoryIcon = '<i class="fas fa-plug"></i>';
                break;
            case 'case':
                categoryName = 'Case';
                categoryIcon = '<i class="fas fa-desktop"></i>';
                break;
            case 'cooling':
                categoryName = 'Cooling';
                categoryIcon = '<i class="fas fa-wind"></i>';
                break;
            default:
                categoryName = 'Component';
                categoryIcon = '<i class="fas fa-puzzle-piece"></i>';
        }
        
        componentModalLabel.textContent = `Select ${categoryName}`;
        modalCategoryIcon.innerHTML = categoryIcon;
        modalCategoryDescription.textContent = `Choose a compatible ${categoryName.toLowerCase()} for your build`;
        
        // Show loading indicator
        componentLoading.style.display = 'block';
        componentCardsWrapper.innerHTML = '';
        
        // Fetch components for this category
        fetch(`/select_component/${category}`)
            .then(response => response.text())
            .then(html => {
                // Hide loading
                componentLoading.style.display = 'none';
                
                // Create a temporary element to parse the HTML
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;
                
                // Extract component cards
                const componentCards = tempDiv.querySelectorAll('.component-card');
                componentCardsWrapper.innerHTML = '';
                
                componentCards.forEach(card => {
                    componentCardsWrapper.appendChild(card.cloneNode(true));
                });
                
                // Re-attach event listeners to add buttons in the component cards
                attachAddButtonListeners();
            })
            .catch(error => {
                console.error('Error loading components:', error);
                componentLoading.style.display = 'none';
                componentCardsWrapper.innerHTML = '<div class="alert alert-danger">Error loading components. Please try again.</div>';
            });
    }
    
    // Attach event listeners to add buttons
    function attachAddButtonListeners() {
        const addButtons = document.querySelectorAll('#componentCardsWrapper .add-component-btn');
        if (!addButtons || addButtons.length === 0) {
            console.log('No add buttons found to attach listeners to');
            return;
        }
        
        addButtons.forEach(button => {
            button.addEventListener('click', function() {
                const componentId = this.getAttribute('data-component-id');
                if (!componentId) {
                    console.error('No component ID found on button');
                    return;
                }
                
                const category = currentCategory;
                if (!category) {
                    console.error('No category selected');
                    return;
                }
                
                // Submit form to add component
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/add_component/${category}/${componentId}`;
                document.body.appendChild(form);
                form.submit();
            });
        });
        
        console.log(`Attached listeners to ${addButtons.length} add buttons`);
    }
    
    // Component selection is handled by the inline JavaScript in builder.html
    // No need to set up these event listeners here as they're already defined in the HTML file
    console.log('Component selection buttons already set up in builder.html');
    
    // Component search functionality - for both mobile and desktop
    // Note: We already defined these variables above, so no need to redefine them here
    
    // Function to handle search filtering
    function handleSearch(searchTerm) {
        searchTerm = searchTerm.toLowerCase();
        const componentCards = document.querySelectorAll('#componentCardsWrapper .component-card');
        
        componentCards.forEach(card => {
            const componentName = card.querySelector('.component-name')?.textContent.toLowerCase() || '';
            const componentDesc = card.querySelector('.component-description')?.textContent.toLowerCase() || '';
            const componentSpecs = card.querySelector('.component-specs')?.textContent.toLowerCase() || '';
            
            if (componentName.includes(searchTerm) || componentDesc.includes(searchTerm) || componentSpecs.includes(searchTerm)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // Desktop search
    if (componentSearchDesktop) {
        componentSearchDesktop.addEventListener('input', function() {
            handleSearch(this.value);
            // Sync mobile search field
            if (componentSearchMobile) {
                componentSearchMobile.value = this.value;
            }
        });
    }
    
    // Mobile search
    if (componentSearchMobile) {
        componentSearchMobile.addEventListener('input', function() {
            handleSearch(this.value);
            // Sync desktop search field
            if (componentSearchDesktop) {
                componentSearchDesktop.value = this.value;
            }
        });
    }
    
    // Site-wide search in search modal
    if (siteSearchInput) {
        siteSearchInput.addEventListener('input', function() {
            console.log('Site search input:', this.value);
            // Site search functionality will be implemented here
        });
    }
    
    // Component sorting functionality
    if (sortOptions && sortOptions.length > 0) {
        sortOptions.forEach(option => {
            option.addEventListener('click', function() {
                const sortBy = this.getAttribute('data-sort');
                const componentCards = Array.from(document.querySelectorAll('#componentCardsWrapper .component-card'));
                const cardsWrapper = document.getElementById('componentCardsWrapper');
                
                if (!cardsWrapper) {
                    console.error('Component cards wrapper not found during sorting');
                    return;
                }
                
                componentCards.sort((a, b) => {
                    if (sortBy === 'name') {
                        const nameA = a.querySelector('.component-name')?.textContent || '';
                        const nameB = b.querySelector('.component-name')?.textContent || '';
                        return nameA.localeCompare(nameB);
                    } else if (sortBy === 'price-asc') {
                        const priceA = parseFloat(a.getAttribute('data-price') || 0);
                        const priceB = parseFloat(b.getAttribute('data-price') || 0);
                        return priceA - priceB;
                    } else if (sortBy === 'price-desc') {
                        const priceA = parseFloat(a.getAttribute('data-price') || 0);
                        const priceB = parseFloat(b.getAttribute('data-price') || 0);
                        return priceB - priceA;
                    } else if (sortBy === 'performance') {
                        const perfA = parseFloat(a.getAttribute('data-performance') || 0);
                        const perfB = parseFloat(b.getAttribute('data-performance') || 0);
                        return perfB - perfA;
                    }
                    return 0;
                });
                
                // Re-append sorted cards
                componentCards.forEach(card => {
                    cardsWrapper.appendChild(card);
                });
            });
        });
    } else {
        console.log('No sort options found on this page');
    }

    // Real-time compatibility checking
    const componentSelections = document.querySelectorAll('.component-select-form');
    if (componentSelections && componentSelections.length > 0) {
        componentSelections.forEach(form => {
            form.addEventListener('change', function(e) {
                if (e.target.matches('input[type="radio"]')) {
                    const categoryInputs = form.querySelectorAll('input[type="radio"]:checked');
                    const currentConfig = {};
                    
                    // Build current config from selected inputs
                    categoryInputs.forEach(input => {
                        const category = input.getAttribute('data-category');
                        if (category) {
                            currentConfig[category] = input.value;
                        }
                    });
                    
                    // Send to server for compatibility check
                    fetch('/api/check_compatibility', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({config: currentConfig}),
                    })
                    .then(response => response.json())
                    .then(data => {
                        const compatibilityAlert = document.getElementById('compatibility-alert');
                        if (!compatibilityAlert) {
                            console.error('Compatibility alert element not found');
                            return;
                        }
                        
                        if (!data.compatible && data.issues && data.issues.length > 0) {
                            let issuesList = '<ul>';
                            data.issues.forEach(issue => {
                                issuesList += `<li>${issue}</li>`;
                            });
                            issuesList += '</ul>';
                            
                            compatibilityAlert.innerHTML = `
                                <div class="alert alert-warning">
                                    <strong>Compatibility Issues:</strong>
                                    ${issuesList}
                                </div>
                            `;
                            compatibilityAlert.style.display = 'block';
                        } else {
                            compatibilityAlert.style.display = 'none';
                        }
                    })
                    .catch(error => {
                        console.error('Error checking compatibility:', error);
                    });
                    
                    // Update price calculation
                    fetch('/api/calculate_price', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({config: currentConfig}),
                    })
                    .then(response => response.json())
                    .then(data => {
                        const priceDisplay = document.getElementById('total-price');
                        if (priceDisplay) {
                            priceDisplay.textContent = `$${data.total.toFixed(2)}`;
                        }
                    })
                    .catch(error => {
                        console.error('Error calculating price:', error);
                    });
                }
            });
        });
    } else {
        console.log('No component selection forms found on this page');
    }

    // Component comparison functionality
    const compareTable = document.getElementById('comparison-table');
    if (compareTable) {
        const compareCheckboxes = document.querySelectorAll('.compare-checkbox');
        if (compareCheckboxes && compareCheckboxes.length > 0) {
            compareCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    // Limit to 3 selections
                    const checkedBoxes = document.querySelectorAll('.compare-checkbox:checked');
                    if (checkedBoxes.length > 3) {
                        this.checked = false;
                        alert('You can compare up to 3 components at a time');
                        return;
                    }
                    
                    // Update comparison table
                    updateComparisonTable();
                });
            });
            
            function updateComparisonTable() {
                const selectedComponents = [];
                const checkedBoxes = document.querySelectorAll('.compare-checkbox:checked');
                
                checkedBoxes.forEach(checkbox => {
                    const componentCard = checkbox.closest('.component-card');
                    if (!componentCard) {
                        console.error('Component card not found for checkbox');
                        return;
                    }
                    
                    const componentNameElement = componentCard.querySelector('.component-name');
                    if (!componentNameElement) {
                        console.error('Component name element not found');
                        return;
                    }
                    
                    const componentData = {
                        name: componentNameElement.textContent,
                        price: componentCard.dataset.price || 0,
                        specs: {}
                    };
                    
                    // Extract all specs
                    const specItems = componentCard.querySelectorAll('.spec-item');
                    specItems.forEach(item => {
                        const specLabel = item.querySelector('.spec-label');
                        const specValue = item.querySelector('.spec-value');
                        
                        if (specLabel && specValue) {
                            const label = specLabel.textContent.trim().replace(':', '');
                            const value = specValue.textContent.trim();
                            componentData.specs[label] = value;
                        }
                    });
                    
                    selectedComponents.push(componentData);
                });
                
                // Build comparison table
                const tableBody = compareTable.querySelector('tbody');
                if (!tableBody) {
                    console.error('Comparison table body not found');
                    return;
                }
                
                tableBody.innerHTML = '';
                
                // Add name row
                const nameRow = document.createElement('tr');
                nameRow.innerHTML = '<th>Name</th>';
                selectedComponents.forEach(comp => {
                    nameRow.innerHTML += `<td>${comp.name}</td>`;
                });
                tableBody.appendChild(nameRow);
                
                // Add price row
                const priceRow = document.createElement('tr');
                priceRow.innerHTML = '<th>Price</th>';
                selectedComponents.forEach(comp => {
                    priceRow.innerHTML += `<td>$${parseFloat(comp.price).toFixed(2)}</td>`;
                });
                tableBody.appendChild(priceRow);
                
                // Add spec rows (ensure all specs from all components are included)
                const allSpecs = new Set();
                selectedComponents.forEach(comp => {
                    Object.keys(comp.specs).forEach(spec => allSpecs.add(spec));
                });
                
                allSpecs.forEach(spec => {
                    const specRow = document.createElement('tr');
                    specRow.innerHTML = `<th>${spec}</th>`;
                    
                    selectedComponents.forEach(comp => {
                        const value = comp.specs[spec] || '-';
                        specRow.innerHTML += `<td>${value}</td>`;
                    });
                    
                    tableBody.appendChild(specRow);
                });
                
                // Show table if components are selected
                if (selectedComponents.length > 0) {
                    compareTable.style.display = 'table';
                    const emptyComparisonElement = document.getElementById('comparison-empty');
                    if (emptyComparisonElement) {
                        emptyComparisonElement.style.display = 'none';
                    }
                } else {
                    compareTable.style.display = 'none';
                    const emptyComparisonElement = document.getElementById('comparison-empty');
                    if (emptyComparisonElement) {
                        emptyComparisonElement.style.display = 'block';
                    } else {
                        console.log('Comparison empty element not found');
                    }
                }
            }
        } else {
            console.log('No comparison checkboxes found on this page');
        }
    } else {
        console.log('Comparison table not found on this page');
    }
    
    // Mobile Panel Functionality is now handled directly in builder.html
    // to avoid any conflicts with duplicate event listeners
    console.log('Mobile panel initialization is handled in builder.html');
});
