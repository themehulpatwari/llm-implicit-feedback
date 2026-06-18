export function isSafari() {
    return /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
}

export function checkBrowser() {
    console.log("Checking browser");
    if (isSafari()) {
        document.body.innerHTML = `
            <div class="browser-warning">
                <h1>Browser Not Supported</h1>
                <p>Safari is not supported for this application.</p>
                <p>Please use Chrome, Firefox, Opera, or Edge to access this page.</p>
            </div>
        `;
    }
}