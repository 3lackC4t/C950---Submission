const mainCard = document.getElementById("content-card");
const runButton = document.getElementById("run-sim");
const aboutButton = document.getElementById("about-btn");

let simulationData = null;

const handleAbout = () => {
    runButton.classList.add('hidden')
    mainCard.className = 'main-content-card about';
};

const handleRun = async () => {
    try {
        const url = 'http://localhost:5000/api/simulate'
        const response = await fetch(url);
        simulationData = await response.json()

        showEndpointsView()
    } catch (error) {
        console.error('Failed to run simulation:', error);
    } 
};

const showFinalState = () => {
    console.log("Show Final State");
}

const showTimeline = () => {
    console.log("Show Timeline");
}

const showSummary = () => {
    console.log("Show summary");
}

const showInitialView = () => {
    console.log("Show Initial View");
}

function showEndpointsView() {
    mainCard.className = 'main-content-card endpoints';
    runButton.classList.add('hidden')
    aboutButton.classList.add('hidden')

    mainCard.appendChild(makeButton('View Final State', 'btn', showFinalState));
    mainCard.appendChild(makeButton('Package Timeline', 'btn', showTimeline));
    mainCard.appendChild(makeButton('Summary Stats', 'btn', showSummary));
    mainCard.appendChild(makeButton('Back', 'btn', showInitialView));

    console.log(simulationData)
}

// Button generator for all the navigation buttons getting thrown around
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

aboutButton.addEventListener('click', handleAbout)
runButton.addEventListener('click', handleRun)