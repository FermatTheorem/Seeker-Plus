class Card {
    constructor(name, depth, parentElement, keyPath = [], allowDelete = true) {
        this.name = name;
        this.depth = depth;
        this.parentElement = parentElement;
        this.element = this.createCardElement();
        this.keyPath = keyPath;
        this.allowDelete = allowDelete
    }

    createCardElement() {
        const section = document.createElement('div');
        section.className = `card card-body mb-3 depth-${this.depth}`;
        this.addHeader(section);
        return section;
    }

    addHeader(section) {
        const header = document.createElement('div');
        header.className = 'config-header d-flex justify-content-between align-items-center';

        const keyElement = document.createElement('h6');
        keyElement.className = 'config-key';
        keyElement.textContent = this.name;
        header.appendChild(keyElement);

        section.appendChild(header);
    }

    addDeleteButton(header) {
        if (!this.allowDelete) return;

        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger btn-sm float-right';
        deleteButton.innerHTML = '&minus;';
        deleteButton.onclick = (event) => {
            event.stopPropagation();
            deleteConfigKey(this.keyPath);
            this.parentElement.removeChild(this.element);
        };
        header.appendChild(deleteButton);
    }
}

class BooleanCard extends Card {
    constructor(name, depth, parentElement, value, keyPath = [], allowDelete=true) {
        super(name, depth, parentElement, keyPath, allowDelete);
        this.value = value;
        this.setupBooleanCard();
    }

    setupBooleanCard() {
        this.element.classList.add('clickable');
        this.addBooleanSwitch(this.element.querySelector('.config-header'));
        this.addDeleteButton(this.element.querySelector('.config-header'));
        this.updateBooleanCardColor(this.value);
        this.element.onclick = (event) => {
            event.stopPropagation();
            this.toggleSwitch();
        };
    }

    addBooleanSwitch(header) {
        const switchContainer = document.createElement('div');
        switchContainer.className = 'custom-control custom-switch';
        switchContainer.style.visibility = 'hidden';

        const switchInput = document.createElement('input');
        switchInput.className = 'custom-control-input';
        switchInput.type = 'checkbox';
        switchInput.id = `switch-${this.name}`;
        switchInput.checked = this.value;

        const switchLabel = document.createElement('label');
        switchLabel.className = 'custom-control-label';
        switchLabel.htmlFor = `switch-${this.name}`;

        switchContainer.appendChild(switchInput);
        switchContainer.appendChild(switchLabel);

        header.appendChild(switchContainer);
    }

    toggleSwitch() {
        const switchInput = this.element.querySelector('.custom-control-input');
        switchInput.checked = !switchInput.checked;
        this.value = switchInput.checked;
        this.updateBooleanCardColor(this.value);
        updateGlobalConfig(this.keyPath, this.value);
    }

    updateBooleanCardColor(isActive) {
        this.element.style.backgroundColor = isActive ? '#d4edda' : '#f8d7da';
    }
}



class InputCard extends Card {
    constructor(name, depth, parentElement, value = '', keyPath = [], allowDelete=true) {
        super(name, depth, parentElement, keyPath, allowDelete);
        this.value = value;
        this.setupInputCard();
    }

    setupInputCard() {
        this.addInputField(this.element.querySelector('.config-header'));
        this.addDeleteButton(this.element.querySelector('.config-header'));
    }

    addInputField(header) {
        const inputContainer = document.createElement('div');
        inputContainer.className = 'config-value mt-2';
        this.element.appendChild(inputContainer);

        const inputElement = document.createElement('input');
        inputElement.type = 'text';
        inputElement.className = 'form-control';
        inputElement.value = this.value;
        inputElement.placeholder = 'Enter text...';
        inputContainer.appendChild(inputElement);

        inputElement.addEventListener('change', (event) => {
            this.value = event.target.value;
            updateGlobalConfig(this.keyPath, this.value);
        });

        this.element.onclick = (event) => {
            event.stopPropagation();
        };
    }
}



class ContainerCard extends Card {
    constructor(name, depth, parentElement, isExpanded = false, keyPath = [], allowDelete=true) {
        super(name, depth, parentElement, keyPath, allowDelete);
        this.children = [];
        this.isExpanded = isExpanded;
        this.setupContainerCard();
    }

    setupContainerCard() {
        this.valueContainer = this.createValueContainer();
        this.addDeleteButton(this.element.querySelector('.config-header'));
        this.element.classList.add('clickable');
        this.element.onclick = (event) => {
            event.stopPropagation();
            this.toggleVisibility();
        };

        if (this.isExpanded) {
            this.toggleVisibility();
        } else {
            this.addChildren(globalConfig, this.depth + 1, this.keyPath);
        }
    }

    createValueContainer() {
        const valueContainer = document.createElement('div');
        valueContainer.className = 'config-value mt-2';
        valueContainer.style.display = 'none';
        this.element.appendChild(valueContainer);
        return valueContainer;
    }

    toggleVisibility() {
        const isVisible = this.valueContainer.style.display !== 'none';
        this.valueContainer.style.display = isVisible ? 'none' : 'block';
    }

    addChildren(config, depth, keyPath) {
        if (!this.valueContainer.hasChildNodes()) {
            const containerConfig = keyPath.reduce((acc, key) => {
                if (!acc[key]) acc[key] = {};
                return acc[key];
            }, globalConfig);

            renderConfig(containerConfig, this.valueContainer, depth + 1, false, keyPath);
            this.addNewCardElement();
        }
    }


    addNewCardElement() {
        if (!this.valueContainer.querySelector('.add-new-container')) {
            const addCard = new AddCard(this.depth + 1, this.valueContainer);
            this.valueContainer.appendChild(addCard.element);
        }
    }

}




class AddCard extends Card {
    constructor(depth, parentElement, keyPath = [], allowDelete=false) {
        super("Add New", depth, parentElement, keyPath, allowDelete);
        this.setupAddCard();
    }

        setupAddCard() {
        this.element.classList.add("add-new-container");
        this.element.innerHTML = '<span class="plus-sign">+</span>';
        this.element.onclick = (event) => {
            event.stopPropagation();
            this.showAddNewCardModal();
        };
    }

    showAddNewCardModal() {
        const modalBackground = document.createElement('div');
        modalBackground.className = 'modal-background';
        document.body.appendChild(modalBackground);

        const modalCard = document.createElement('div');
        modalCard.className = 'modal-card card';
        modalCard.innerHTML = `
            <h5 class="text-center font-weight-bold mb-3">Add a new parameter</h5>
            <div id="error-message" class="text-danger text-center mb-2" style="display: none;"></div>
            <input type="text" class="form-control mb-2" placeholder="Parameter Name" id="new-param-name">
            <select class="form-control mb-3" id="new-param-type">
                <option value="text">Text</option>
                <option value="boolean">Boolean</option>
                <option value="container">Container</option>
            </select>
            <div class="text-center">
                <button class="btn btn-success btn-block mb-2">Add</button>
                <button class="btn btn-secondary btn-block">Cancel</button>
            </div>
        `;
        document.body.appendChild(modalCard);

        const errorMessageElement = modalCard.querySelector('#error-message');
        modalCard.querySelector('.btn-success').onclick = () => this.addNewCard(modalBackground, modalCard, errorMessageElement);
        modalCard.querySelector('.btn-secondary').onclick = () => this.closeModal(modalBackground, modalCard);
        modalBackground.onclick = () => this.closeModal(modalBackground, modalCard);
    }

    addNewCard(modalBackground, modalCard, errorMessageElement) {
        const name = document.getElementById('new-param-name').value.trim();
        const type = document.getElementById('new-param-type').value;

        if (!name) {
            errorMessageElement.textContent = 'Please enter a name for the parameter.';
            errorMessageElement.style.display = 'block';
            return;
        } else {
            errorMessageElement.style.display = 'none';
        }

        const newKeyPath = [...this.keyPath, name];
        let newCard;
        switch (type) {
            case 'text':
                newCard = new InputCard(name, this.depth + 1, this.parentElement, '', newKeyPath);
                break;
            case 'boolean':
                newCard = new BooleanCard(name, this.depth + 1, this.parentElement, false, newKeyPath);
                break;
            case 'container':
                newCard = new ContainerCard(name, this.depth + 1, this.parentElement, true, newKeyPath);
                break;
        }

        if (newCard) {
            this.parentElement.insertBefore(newCard.element, this.element);
            updateGlobalConfig(newKeyPath, newCard instanceof ContainerCard ? {} : newCard.value);
            if (newCard instanceof ContainerCard) {
                newCard.addChildren({}, newCard.depth, newKeyPath);
            }
        }

        this.closeModal(modalBackground, modalCard);
    }

    closeModal(modalBackground, modalCard) {
        document.body.removeChild(modalBackground);
        document.body.removeChild(modalCard);
    }
}

function renderConfig(config, parentElement, depth = 0, isRoot = true, parentKeyPath = []) {
    parentElement.innerHTML = '';

    const nonContainerKeys = [];
    const containerKeys = [];

    Object.entries(config).forEach(([key, value]) => {
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            containerKeys.push(key);
        } else {
            nonContainerKeys.push(key);
        }
    });

    const createCard = (key, value, keyPath) => {
        if (typeof value === 'boolean') {
            return new BooleanCard(key, depth, parentElement, value, keyPath);
        } else {
            return new InputCard(key, depth, parentElement, value.toString(), keyPath);
        }
    };

    nonContainerKeys.forEach(key => {
        const value = config[key];
        const keyPath = [...parentKeyPath, key];
        const card = createCard(key, value, keyPath);
        parentElement.appendChild(card.element);
    });

    containerKeys.forEach(key => {
        const value = config[key];
        const keyPath = [...parentKeyPath, key];
        const card = new ContainerCard(key, depth, parentElement, false, keyPath);
        if (!isRoot) {
            card.addChildren(value, depth + 1, keyPath);
        }
        parentElement.appendChild(card.element);
    });

    if (isRoot || parentElement instanceof HTMLDivElement) {
        const addCard = new AddCard(depth, parentElement, parentKeyPath);
        parentElement.appendChild(addCard.element);
    }

    createButtons();
}

let globalConfig = {};

function updateGlobalConfig(keyPath, value) {
    let currentLevel = globalConfig;
    for (let i = 0; i < keyPath.length - 1; i++) {
        if (currentLevel[keyPath[i]] === undefined) {
            currentLevel[keyPath[i]] = {};
        }
        currentLevel = currentLevel[keyPath[i]];
    }
    currentLevel[keyPath[keyPath.length - 1]] = value;
}

function deleteConfigKey(keyPath) {
    let currentLevel = globalConfig;
    for (let i = 0; i < keyPath.length - 1; i++) {
        if (currentLevel[keyPath[i]] === undefined) {
            return;
        }
        currentLevel = currentLevel[keyPath[i]];
    }
    delete currentLevel[keyPath[keyPath.length - 1]];
}

function createButtons() {
    var buttonsContainer = document.createElement('div');
    buttonsContainer.classList.add('buttons-container');

    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    saveButton.classList.add('btn', 'btn-success', 'btn-save-config');
    saveButton.onclick = function() {
        fetch('/save-config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(globalConfig)
        })
        .then(response => {
            if(response.ok) {
                return response.json();
            } else {
                console.error('Save failed', response);
            }
        })
        .catch(error => console.error('Error saving config:', error));
    };

    var cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.classList.add('btn', 'btn-danger', 'btn-cancel-config');
    cancelButton.addEventListener('click', function() {
        fetchConfig();
    });

    buttonsContainer.appendChild(saveButton);
    buttonsContainer.appendChild(cancelButton);

    document.getElementById('Config').appendChild(buttonsContainer);
}

function fetchConfig() {
    fetch('/get-config')
        .then(response => response.json())
        .then(config => {
            globalConfig = config; // Update the shared configuration
            renderConfig(globalConfig, document.getElementById('config-container'));
        });
}

function makeMainPage() {
    fetch('/get-config')
        .then(response => response.json())
        .then(config => {
            renderMainPage(config, document.getElementById('main-container'));
        });
}

class LogCard extends Card {
    constructor(name, depth, parentElement, logFileName, keyPath = [], allowDelete=false) {
        super(name, depth, parentElement, keyPath, allowDelete);
        this.logFileName = logFileName;
        this.setupLogCard();
    }

    setupLogCard() {
        this.valueContainer = this.createValueContainer();
        this.element.classList.add('clickable');
        this.element.onclick = (event) => {
            event.stopPropagation();
            this.toggleVisibility();
        };
    }

    createValueContainer() {
        const valueContainer = document.createElement('div');
        valueContainer.className = 'config-value mt-2';
        valueContainer.style.display = 'none';
        const iframe = document.createElement('iframe');
        iframe.src = this.logFileName;
        iframe.style.width = '100%';
        iframe.style.height = '400px';
        valueContainer.appendChild(iframe);
        this.element.appendChild(valueContainer);
        return valueContainer;
    }

    toggleVisibility() {
        const isVisible = this.valueContainer.style.display !== 'none';
        this.valueContainer.style.display = isVisible ? 'none' : 'block';
    }
}

function openPage(pageName, elmnt) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(pageName).style.display = "block";
    elmnt.className += " active";
}

// Fetch and render the main page content
function fetchMainPageConfig() {
    fetch('/get-config')
        .then(response => response.json())
        .then(config => {
            renderMainPage(config, document.getElementById('main-container'));
        });
}

function renderMainPage(config, parentElement) {
    const targetCard = new InputCard('Target', 0, parentElement, value = config["Target"] || '', keyPath = ["Target"], allowDelete=false);
    parentElement.appendChild(targetCard.element);

    // Application log
    const appLogCard = new LogCard('Application Log', 0, parentElement, 'output/application.log');
    parentElement.appendChild(appLogCard.element);

    // Module logs
    Object.entries(config.Modules || {}).forEach(([moduleName, moduleConfig]) => {
        if (moduleConfig.enabled) {
            const moduleLogCard = new LogCard(`${moduleName} Log`, 0, parentElement, `${moduleName}.log`);
            parentElement.appendChild(moduleLogCard.element);
        }
    });

    // Start button
    const startButton = document.createElement('button');
    startButton.textContent = 'Start';
    startButton.classList.add('btn', 'btn-primary', 'btn-start-process');
    startButton.onclick = function() {
        fetch('/process')
            .then(response => response.text())
            .catch(error => console.error('Error starting process:', error));
    };
    parentElement.appendChild(startButton);
}

document.addEventListener('DOMContentLoaded', function() {
    // Fetch and setup for Config page
    fetchConfig();
    makeMainPage();
    openPage('Main', document.getElementsByClassName('tablinks')[0]);
});


