let startTime;
const REQUIRED_TIME = 4 * 60 * 1000; // 240 seconds in milliseconds

export function startStopwatch() {
    startTime = Date.now();
    setupFinishedButton();
}

function setupFinishedButton() {
    const finishedButton = document.getElementById('finished');
    const submitButton = finishedButton.querySelector('button');
    
    submitButton.addEventListener('click', (e) => {
        const timeSpent = Date.now() - startTime;
        if (timeSpent < REQUIRED_TIME) {
            e.preventDefault();
            const timeLeft = Math.ceil((REQUIRED_TIME - timeSpent) / 1000);
            alert(`Please spend more time reviewing and asking questions. ${timeLeft} seconds remaining.`);
        }
    });
}


export function getCurrentTimestamp() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0'); 
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

export function getCurrentTimestampUTC() {
    const now = new Date();
    const year = now.getUTCFullYear();
    const month = String(now.getUTCMonth() + 1).padStart(2, '0'); 
    const day = String(now.getUTCDate()).padStart(2, '0');
    const hours = String(now.getUTCHours()).padStart(2, '0');
    const minutes = String(now.getUTCMinutes()).padStart(2, '0');
    const seconds = String(now.getUTCSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}