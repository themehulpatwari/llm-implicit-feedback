// Function to initialize inactivity tracking
function initInactivityTimer() {
    const TIMEOUT_DURATION = 30 * 60 * 1000; // 30 minutes
    const REDIRECT_URL = '/public/webpage/login.php';

    let inactivityTimer;

    function resetTimer() {
        clearTimeout(inactivityTimer);
        inactivityTimer = setTimeout(() => {
            window.location.href = REDIRECT_URL;
        }, TIMEOUT_DURATION);
    }

    document.addEventListener('mousemove', resetTimer);
    document.addEventListener('keydown', resetTimer);
    document.addEventListener('click', resetTimer);
    document.addEventListener('scroll', resetTimer);

    resetTimer();
}

initInactivityTimer();    
