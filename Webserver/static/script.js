document.addEventListener('DOMContentLoaded', function() {
    fetchConfig();

    function fetchConfig() {
        fetch('/get-config')
            .then(response => response.json())
            .then(config => {
                renderConfig(config, document.getElementById('config-container'));
            })
            .catch(error => console.error('Error fetching config:', error));
    }

    function renderConfig(config, parentElement, depth = 0) {
        const primitiveContainer = document.createElement('div');
        const nestedContainer = document.createElement('div');

        for (const key in config) {
            const value = config[key];
            const targetContainer = typeof value === 'object' && value !== null ? nestedContainer : primitiveContainer;

            const section = document.createElement('div');
            section.className = `card card-body mb-3 depth-${depth}`;
            (typeof value === 'object' && value !== null ? nestedContainer : primitiveContainer).appendChild(section);

            const header = document.createElement('div');
            header.className = 'config-header d-flex justify-content-between align-items-center';
            section.appendChild(header);

            const keyElement = document.createElement('h6');
            keyElement.className = 'config-key';
            keyElement.textContent = key;
            header.appendChild(keyElement);

            const valueContainer = document.createElement('div');
            valueContainer.className = 'config-value mt-2';
            section.appendChild(valueContainer);

            if (typeof value === 'object' && value !== null) {
                section.classList.add('clickable');
                section.onclick = function(event) {
                    event.stopPropagation();
                    if (valueContainer.style.display === 'none') {
                        collapseSiblings(section);
                    }
                    toggleVisibility(valueContainer, section);
                };
                valueContainer.style.display = 'none';
                renderConfig(value, valueContainer, depth + 1);
            } else {
                applyStopPropagation(section);
                if (typeof value === 'boolean') {
                    const switchElement = createBooleanSwitch(key, value);
                    switchElement.style.visibility = 'hidden'; // Hide the switch
                    updateBooleanCardColor(section, value);
                    header.appendChild(switchElement);
                    section.classList.add('clickable');
                    section.onclick = function(event) {
                        event.stopPropagation();
                        switchElement.querySelector('input').checked = !switchElement.querySelector('input').checked;
                        updateBooleanCardColor(section, switchElement.querySelector('input').checked);
                    };
                } else {
                    const inputElement = typeof value === 'string' && value.length > 30 ?
                        document.createElement('textarea') : document.createElement('input');
                    inputElement.className = 'form-control';
                    inputElement.value = typeof value === 'string' ? value : JSON.stringify(value);
                    valueContainer.appendChild(inputElement);

                }
            }

            const deleteButton = createDeleteButton();
            header.appendChild(deleteButton);
            deleteButton.onclick = function(event) {
                event.stopPropagation();
                (typeof config[key] === 'object' && config[key] !== null ? nestedContainer : primitiveContainer).removeChild(section);
            };

        }

        parentElement.appendChild(primitiveContainer);
        parentElement.appendChild(nestedContainer);

        const addNewContainer = createAddNewContainer(depth, parentElement);
        parentElement.appendChild(addNewContainer);

    }

    function toggleVisibility(container, header) {
        const isVisible = container.style.display !== 'none';
        container.style.display = isVisible ? 'none' : 'block';
    }

    function applyStopPropagation(element) {
        element.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    }


    function createBooleanSwitch(key, value) {
        const switchContainer = document.createElement('div');
        switchContainer.className = 'custom-control custom-switch';

        const switchInput = document.createElement('input');
        switchInput.className = 'custom-control-input';
        switchInput.type = 'checkbox';
        switchInput.id = `switch-${key}`;
        switchInput.checked = value;

        const switchLabel = document.createElement('label');
        switchLabel.className = 'custom-control-label';
        switchLabel.htmlFor = `switch-${key}`;

        switchContainer.appendChild(switchInput);
        switchContainer.appendChild(switchLabel);

        return switchContainer;
    }

    function collapseSiblings(element) {
        let sibling = element.parentNode.firstChild;
        while (sibling) {
            if (sibling !== element && sibling.classList.contains('card')) {
                sibling.querySelector('.config-value').style.display = 'none';
            }
            sibling = sibling.nextSibling;
        }
    }

    function toggleSwitch(switchElement) {
        const input = switchElement.querySelector('input');
        input.checked = !input.checked;
    }

    function createDeleteButton() {
        const button = document.createElement('button');
        button.className = 'btn btn-danger btn-sm float-right';
        button.innerHTML = '&minus;';
        return button;
    }

    function updateBooleanCardColor(section, isActive) {
        section.style.backgroundColor = isActive ? '#d4edda' : '#f8d7da'; // Green for true, red for false
    }

    function createAddNewContainer(depth, parentElement) {
        const addContainer = document.createElement('div');
        addContainer.className = `card card-body mb-3 depth-${depth} add-new-container`;
        addContainer.innerHTML = '<span class="plus-sign">+</span>';
        addContainer.onclick = function() {
            event.stopPropagation()
            showAddNewCardModal(parentElement, depth);
        };
        return addContainer;
    }

    function showAddNewCardModal(parentElement, depth) {
        const modalBackground = document.createElement('div');
        modalBackground.className = 'modal-background';
        document.body.appendChild(modalBackground);

        const modalCard = document.createElement('div');
        modalCard.className = 'modal-card card';
        modalCard.innerHTML = `
            <h5 class="text-center font-weight-bold mb-3">Add a new parameter</h5>
            <input type="text" class="form-control mb-2" placeholder="Parameter Name">
            <select class="form-control mb-3">
                <option value="text">Text</option>
                <option value="boolean">Boolean</option>
                <option value="container">Container</option>
            </select>
            <div class="text-center">
                <button class="btn btn-success btn-block mb-2" onclick="addNewCard(this.parentElement.parentElement, parentElement, depth)">Add</button>
                <button class="btn btn-secondary btn-block" onclick="closeModal()">Cancel</button>
            </div>
        `;

        const addButton = modalCard.querySelector('.btn-success');
        addButton.onclick = addNewCard.bind(addButton, modalCard, parentElement, depth);

        document.body.appendChild(modalCard);

        modalBackground.onclick = closeModal;
    }

    window.closeModal = function() {
        document.body.removeChild(document.querySelector('.modal-background'));
        document.body.removeChild(document.querySelector('.modal-card'));
    }

    window.addNewCard = function(modal, parentElement, depth) {
        event.preventDefault();

        const nameInput = modal.querySelector('input[type="text"]');
        const typeSelect = modal.querySelector('select');
        const name = nameInput.value.trim();
        const type = typeSelect.value;


        // Check if the name is not empty
        if (name === '') {
            alert('Please enter a name for the parameter.');
            return;
        }

        // Create and add the new card
        addCardToLevel(name, type, parentElement, depth);
        closeModal();
    };

    function addCardToLevel(name, type, parentElement, depth) {
        const section = document.createElement('div');
        section.className = `card card-body mb-3 depth-${depth}`;
        parentElement.insertBefore(section, parentElement.lastElementChild); // Insert before the add new container

        const header = document.createElement('div');
        header.className = 'config-header d-flex justify-content-between align-items-center';
        section.appendChild(header);

        const keyElement = document.createElement('h6');
        keyElement.className = 'config-key';
        keyElement.textContent = name;
        header.appendChild(keyElement);

        const valueContainer = document.createElement('div');
        valueContainer.className = 'config-value mt-2';
        section.appendChild(valueContainer);

        // Create different types of cards based on the selected type
        if (type === 'text') {
            const inputElement = document.createElement('input');
            inputElement.className = 'form-control';
            inputElement.placeholder = 'Enter text...';
            valueContainer.appendChild(inputElement);
        } else if (type === 'boolean') {
            const switchElement = createBooleanSwitch(name, false);
            switchElement.style.visibility = 'hidden'; // Keep the switch hidden
            updateBooleanCardColor(section, false);
            header.appendChild(switchElement);
            section.classList.add('clickable');
        } else if (type === 'container') {
            valueContainer.style.display = 'none'; // Initially hidden
            section.classList.add('clickable');
            section.onclick = function(event) {
                event.stopPropagation();
                toggleVisibility(valueContainer, section);
            };

            const nestedContainer = document.createElement('div');
            valueContainer.appendChild(nestedContainer);

            // Recursively call renderConfig for the new container card
            renderConfig({}, nestedContainer, depth + 1);

        }
        section.onclick = function(event) {
            event.stopPropagation();
            const input = switchElement.querySelector('input');
            input.checked = !input.checked;
            updateBooleanCardColor(section, input.checked);
        };
        // Add the delete button
        const deleteButton = createDeleteButton();
        header.appendChild(deleteButton);
        deleteButton.onclick = function(event) {
            event.stopPropagation();
            parentElement.removeChild(section);
        };
    }


});
