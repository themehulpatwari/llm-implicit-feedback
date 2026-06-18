let startTime = performance.now();
let pausedTime = 0;
let totalPausedTime = 0;
let isPaused = false;

document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        isPaused = true;
        pausedTime = performance.now();
    } else {
        if (isPaused) {
            totalPausedTime += performance.now() - pausedTime;
            isPaused = false;
        }
    }
});

export function getPageTime() {
    if (isPaused) {
        return pausedTime - startTime - totalPausedTime;
    }
    return performance.now() - startTime - totalPausedTime;
}
