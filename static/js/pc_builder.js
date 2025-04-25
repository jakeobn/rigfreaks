document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Component selection interface variables
    const componentSelectionContainer = document.getElementById('componentSelectionContainer');
    const componentDropdownBtns = document.querySelectorAll('.component-dropdown-btn');
    const closeComponentSelectionBtn = document.getElementById('closeComponentSelection');
    const cancelComponentSelectionBtn = document.getElementById('cancelComponentSelection');
    const componentSearch = document.getElementById('componentSearch');
    const sortOptions = document.querySelectorAll('.sort-option');
    let currentCategory = '';

    // Helper function to load components for a category
    function loadComponentsForCategory(category) {
        const componentCardsWrapper = document.getElementById('componentCardsWrapper');
        const componentLoading = document.getElementById('component-loading');
        const modalCategoryIcon = document.getElementById('modalCategoryIcon');
        const componentModalLabel = document.getElementById('componentModalLabel');
        const modalCategoryDescription = document.getElementById('modalCategoryDescription');
        
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
        addButtons.forEach(button => {
            button.addEventListener('click', function() {
                const componentId = this.getAttribute('data-component-id');
                const category = currentCategory;
                
                // Submit form to add component
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/add_component/${category}/${componentId}`;
                document.body.appendChild(form);
                form.submit();
            });
        });
    }
    
    // Show component selection
    componentDropdownBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            currentCategory = this.getAttribute('data-category');
            componentSelectionContainer.classList.remove('d-none');
            loadComponentsForCategory(currentCategory);
        });
    });
    
    // Hide component selection
    if (closeComponentSelectionBtn) {
        closeComponentSelectionBtn.addEventListener('click', function() {
            componentSelectionContainer.classList.add('d-none');
        });
    }
    
    if (cancelComponentSelectionBtn) {
        cancelComponentSelectionBtn.addEventListener('click', function() {
            componentSelectionContainer.classList.add('d-none');
        });
    }
    
    // Component search functionality
    if (componentSearch) {
        componentSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
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
        });
    }
    
    // Component sorting functionality
    sortOptions.forEach(option => {
        option.addEventListener('click', function() {
            const sortBy = this.getAttribute('data-sort');
            const componentCards = Array.from(document.querySelectorAll('#componentCardsWrapper .component-card'));
            const cardsWrapper = document.getElementById('componentCardsWrapper');
            
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

    // Real-time compatibility checking
    const componentSelections = document.querySelectorAll('.component-select-form');
    componentSelections.forEach(form => {
        form.addEventListener('change', function(e) {
            if (e.target.matches('input[type="radio"]')) {
                const categoryInputs = form.querySelectorAll('input[type="radio"]:checked');
                const currentConfig = {};
                
                // Build current config from selected inputs
                categoryInputs.forEach(input => {
                    currentConfig[input.getAttribute('data-category')] = input.value;
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
                    if (!data.compatible && data.issues.length > 0) {
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

    // Component comparison functionality
    const compareTable = document.getElementById('comparison-table');
    if (compareTable) {
        const compareCheckboxes = document.querySelectorAll('.compare-checkbox');
        
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
                const componentData = {
                    name: componentCard.querySelector('.component-name').textContent,
                    price: componentCard.dataset.price,
                    specs: {}
                };
                
                // Extract all specs
                const specItems = componentCard.querySelectorAll('.spec-item');
                specItems.forEach(item => {
                    const label = item.querySelector('.spec-label').textContent.trim().replace(':', '');
                    const value = item.querySelector('.spec-value').textContent.trim();
                    componentData.specs[label] = value;
                });
                
                selectedComponents.push(componentData);
            });
            
            // Build comparison table
            const tableBody = compareTable.querySelector('tbody');
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
                document.getElementById('comparison-empty').style.display = 'none';
            } else {
                compareTable.style.display = 'none';
                document.getElementById('comparison-empty').style.display = 'block';
            }
        }
    }
});
