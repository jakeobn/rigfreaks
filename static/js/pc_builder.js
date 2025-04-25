document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

    // Handle component selection filtering
    const componentFilter = document.getElementById('component-filter');
    if (componentFilter) {
        componentFilter.addEventListener('input', function() {
            const filterValue = this.value.toLowerCase();
            const componentCards = document.querySelectorAll('.component-card');
            
            componentCards.forEach(card => {
                const componentName = card.querySelector('.component-name').textContent.toLowerCase();
                const componentSpecs = card.querySelector('.component-specs').textContent.toLowerCase();
                
                if (componentName.includes(filterValue) || componentSpecs.includes(filterValue)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Sort component list
    const sortSelect = document.getElementById('component-sort');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const sortValue = this.value;
            const componentContainer = document.querySelector('.component-container');
            const componentCards = Array.from(document.querySelectorAll('.component-card'));
            
            componentCards.sort((a, b) => {
                if (sortValue === 'price-low') {
                    const priceA = parseFloat(a.dataset.price || 0);
                    const priceB = parseFloat(b.dataset.price || 0);
                    return priceA - priceB;
                } else if (sortValue === 'price-high') {
                    const priceA = parseFloat(a.dataset.price || 0);
                    const priceB = parseFloat(b.dataset.price || 0);
                    return priceB - priceA;
                } else if (sortValue === 'name-asc') {
                    const nameA = a.querySelector('.component-name').textContent;
                    const nameB = b.querySelector('.component-name').textContent;
                    return nameA.localeCompare(nameB);
                } else if (sortValue === 'name-desc') {
                    const nameA = a.querySelector('.component-name').textContent;
                    const nameB = b.querySelector('.component-name').textContent;
                    return nameB.localeCompare(nameA);
                }
                return 0;
            });
            
            componentCards.forEach(card => {
                componentContainer.appendChild(card);
            });
        });
    }

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
