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
            It demonstrates the use of a greedy algorithm for package prioritization and an implementation of
            the 'Nearest Neighbor' algorithm for route selection.
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

    let delivery = null;

    // Captures if delivery time is not available (not delivered)
    if (packageData.DELIVERY_TIME != null) {
        delivery = packageData.DELIVERY_TIME;
    } else {
        delivery = "N/A";
    }

    card.innerHTML = `
        <div class='package-header'>
            <h3>Package #${packageData.ID}</h3>
            <span class="status-badge status-${packageData.STATUS.toLowerCase()}">
                ${packageData.STATUS}
            </span>
        </div>
        <div class="package-details" style="text-align: left;">
            <p><strong>Address:</strong>${packageData.TRUCK_ID || 'N/A'}</p>
            <p><strong>Address:</strong>${packageData.ADDRESS || 'N/A'}</p>
            <p><strong>Weight:</strong>${packageData.WEIGHT || 'N/A'}</p>
            <p><strong>Note:</strong>${packageData.NOTE || 'N/A'}</p>
            <p><strong>Delivered:</strong>${delivery}</p>
            <p><strong>Deadline:</strong>${(packageData.DEADLINE).split("T")[1] || 'N/A'}</p>
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
    mainCard.className = "main-content-card timeline";
    mainCard.innerHTML = "";

    // Basic description
    const title = document.createElement('h2');
    title.textContent = "Package Status Timeline";
    title.style.cssText = 'font-size: 2.4rem; color: #2d3748; margin-bottom: 1rem; text-align: center;';
    mainCard.appendChild(title);

    const subtitle = document.createElement('p');
    subtitle.textContent = "Select a timestamp from the following in order to view status of all packages at that time";
    subtitle.style.cssText = 'font-size: 1.6rem; color: #4a5568; margin-bottom: 2rem; text-align: center;';
    mainCard.appendChild(subtitle); 

    // Create buttons for selected timestamps
    let packageHistory = simulationData.package_history;
    Object.keys(packageHistory).forEach(timestamp => {
        if (timestamp != "FINAL") {
            const timeStampSelect = makeButton(`${timestamp}:00`, "btn");
            timeStampSelect.addEventListener("click", () => showTimestampView(timestamp));
            mainCard.appendChild(timeStampSelect);
        }
    });

    mainCard.appendChild(makeButton('Back', 'btn', showEndpointsView));
}

function showTimestampView(timeStamp) {
    mainCard.innerHTML = "";

    let packages = simulationData.package_history[timeStamp].history;
        
    // Create scrollable container
    const scrollContainer = document.createElement('div');
    scrollContainer.className = 'package-scroll-container';
   
    // Generate cards from simulation data
    Object.keys(packages).forEach(pkgId => {
        const card = createPackageCard(packages[pkgId]);
        scrollContainer.appendChild(card);
    });
    
    mainCard.appendChild(scrollContainer);
    mainCard.appendChild(makeButton('Back', 'btn', showTimeline));

}

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
    
    // Show final miles driven
    const totalMiles = document.createElement('p');
    totalMiles.textContent = `Total Miles Driven: ${Math.round(simulationData.total_miles)}`;
    totalMiles.style.cssText = 'font-size: 1.6rem; color: #4a5568; margin-bottom: 2rem; text-align: center;';
    mainCard.appendChild(totalMiles);    

    // Add subtitle
    const subtitle = document.createElement('p');
    subtitle.textContent = 'Choose what you\'d like to view:';
    subtitle.style.cssText = 'font-size: 1.6rem; color: #4a5568; margin-bottom: 2rem; text-align: center;';
    mainCard.appendChild(subtitle);    

    // Add buttons
    mainCard.appendChild(makeButton('View Final State', 'btn', showFinalState));
    mainCard.appendChild(makeButton('Package Timeline', 'btn', showTimeline));
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