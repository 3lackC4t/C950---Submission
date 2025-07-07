const mainCard = document.getElementById("content-card");
const runButton = document.getElementById("run-sim");
const aboutButton = document.getElementById("about-btn");

let simulationData = null;

const handleAbout = () => {
    runButton.classList.add('hidden');
    aboutButton.classList.add('hidden');
    mainCard.className = 'main-content-card about';
    
    // Clear existing content and add about info
    mainCard.innerHTML = `
        <h2 style="font-size: 2.4rem; color: #2d3748; margin-bottom: 1.5rem;">About WGUPS</h2>
        <p style="font-size: 1.6rem; color: #4a5568; line-height: 1.6; margin-bottom: 2rem;">
            This is a routing simulation system for Western Governors University Parcel Service. 
            It demonstrates various routing algorithms and package delivery optimization strategies.
        </p>
    `;
    
    mainCard.appendChild(makeButton('Back', 'btn', showInitialView));
};

const handleRun = async () => {
    try {
        // Show loading state
        runButton.textContent = 'Running...';
        runButton.disabled = true;
        
        const url = 'http://localhost:5000/api/simulate';
        const response = await fetch(url);
        simulationData = await response.json();

        showEndpointsView();
    } catch (error) {
        console.error('Failed to run simulation:', error);
        runButton.textContent = 'Run Sim!';
        runButton.disabled = false;
        alert('Failed to run simulation. Please try again.');
    } 
};

const showFinalState = () => {
    mainCard.className = 'main-content-card final-state';
    mainCard.innerHTML = '';
    
    // Add header
    const header = document.createElement('div');
    header.innerHTML = `
        <h2>Final Package States</h2>
        <p>All packages and their delivery status</p>
    `;
    mainCard.appendChild(header);
    
    // Create scrollable container
    const scrollContainer = document.createElement('div');
    scrollContainer.className = 'package-scroll-container';
   
    let packages = simulationData.package_history.FINAL.history
    // Generate cards from simulation data
    Object.keys(packages).forEach(pkgId => {
        const card = createPackageCard(packages[pkgId]);
        scrollContainer.appendChild(card);
    });
    
    mainCard.appendChild(scrollContainer);
    mainCard.appendChild(makeButton('Back', 'btn', showEndpointsView));
};

function createPackageCard(packageData) {
    const card = document.createElement('div');
    card.className = 'package-card';
    card.packageData = packageData;

    card.innerHTML = `
        <div class='package-header'>
            <h3>Package #${packageData.ID}</h3>
            <span class="status-badge status-${packageData.STATUS.toLowerCase()}">
                ${packageData.STATUS}
            </span>
        </div>
        <div class="package-details">
            <p><strong>Address:</strong>${packageData.ADDRESS || 'N/A'}</p>
            <p><strong>Weight:</strong>${packageData.WEIGHT || 'N/A'}</p>
            <p><strong>Deadline:</strong>${packageData.DEADLINE || 'N/A'}</p>
        </div>
        <div class="package-log hidden">
        
        </div>
    `;

    card.addEventListener('click', () => togglePackageLog(card));

    return card;
}

function togglePackageLog(card) {
    const logContainer = card.querySelector('.package-log');
    const arrow = card.querySelector('.expand-arrow');
    const packageData = card.packageData

    if (logContainer.classList.contains('hidden')) {
        const package_log = packageData.PACKAGE_LOG;
        let logHTML = '<div class="log-header"><h5>Package Log:</h5><>';
        
        package_log.forEach(log => {
            console.log(log);
            logHTML += `<div class="log-entry"><p class="log-text">${log}</p></div>`;
        });

        logContainer.innerHTML = logHTML;
        logContainer.classList.remove('hidden');
        arrow.textContent = '▼';
        card.classList.add('expanded');
    } else {
        logContainer.classList.add('hidden');
        arrow.textContent = '▶';
        card.classList.remove('expanded');
    }
}

const showTimeline = () => {
    console.log("Show Timeline");
    // TODO: Implement timeline view
};

const showSummary = () => {
    console.log("Show summary");
    // TODO: Implement summary view
};

const showInitialView = () => {
    // Reset to initial state
    mainCard.className = 'main-content-card';
    mainCard.innerHTML = '';
    
    // Re-add the original buttons
    mainCard.appendChild(makeButton('Run Sim!', 'btn', handleRun));
    mainCard.appendChild(makeButton('About', 'btn', handleAbout));
    
    // Re-assign the event listeners since we recreated the buttons
    const newRunButton = mainCard.querySelector('button');
    const newAboutButton = mainCard.querySelectorAll('button')[1];
    
    newRunButton.id = 'run-sim';
    newAboutButton.id = 'about-btn';
};

function showEndpointsView() {
    mainCard.className = 'main-content-card endpoints';
    runButton.classList.add('hidden');
    aboutButton.classList.add('hidden');
    
    // Clear existing content
    mainCard.innerHTML = '';
    
    // Add title
    const title = document.createElement('h2');
    title.textContent = 'Simulation Complete!';
    title.style.cssText = 'font-size: 2.4rem; color: #2d3748; margin-bottom: 1rem; text-align: center;';
    mainCard.appendChild(title);
    
    // Add subtitle
    const subtitle = document.createElement('p');
    subtitle.textContent = 'Choose what you\'d like to view:';
    subtitle.style.cssText = 'font-size: 1.6rem; color: #4a5568; margin-bottom: 2rem; text-align: center;';
    mainCard.appendChild(subtitle);
    
    // Add buttons - these will be equally distributed due to flexbox
    mainCard.appendChild(makeButton('View Final State', 'btn', showFinalState));
    mainCard.appendChild(makeButton('Package Timeline', 'btn', showTimeline));
    mainCard.appendChild(makeButton('Summary Stats', 'btn', showSummary));
    mainCard.appendChild(makeButton('Back', 'btn', showInitialView));
}

// Button generator for all the navigation buttons
function makeButton(textContent, classes, callBack = null) {
    const newBtn = document.createElement('button');
    newBtn.textContent = textContent;

    if (Array.isArray(classes)) {
        newBtn.classList.add(...classes);
    } else {
        newBtn.classList.add(classes);
    }

    if (callBack) {
        newBtn.addEventListener('click', callBack);
    }
    
    return newBtn;
}

// Initial event listeners
aboutButton.addEventListener('click', handleAbout);
runButton.addEventListener('click', handleRun);