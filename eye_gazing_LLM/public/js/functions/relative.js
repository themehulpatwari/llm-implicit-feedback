// export function relatively(x,y){ //input getBoundingClientRect()
//     return {x: x >= rect.left && x <= rect.right ? x - rect.left: -1, y: y >= rect.top && y <=rect.bottom ? y - rect.top: -1}
// }

let test = true;

// export function relativelyVar(x,y, dom){ //input getBoundingClientRect()
//     const rect = dom.getBoundingClientRect();
//     // return {x: x >= rect.left && x <= rect.right ? x - rect.left: -1, y: y >= rect.top && y <=rect.bottom ? y - rect.top: -1}
//     // const dom = dom.scrollTop;

//     // return {x: x >= rect.left && x <= rect.right ? x - rect.left: -1, y: y >= rect.top && y <=rect.bottom ? y - rect.top: -1}

//     // const rect = scrollableDiv.getBoundingClientRect();

//     const isOutsideX = x < rect.left || x > rect.right;
//     const isOutsideY = y < rect.top || y > rect.bottom;

//     // Calculate the position of the dot relative to the <div>
//     const relativeX = x - rect.left + dom.scrollLeft;
//     const relativeY = y - rect.top + dom.scrollTop;

//     return { x: isOutsideX ? -1 : relativeX, y: isOutsideY ? -1 : relativeY };
// }

/**
 * Calculate relative coordinates within a DOM element
 * @param {number} x - Client X coordinate
 * @param {number} y - Client Y coordinate
 * @param {HTMLElement} dom - Target DOM element
 * @returns {Object} Relative coordinates or -1 if outside
 */

export function relativelyVar(x, y, dom, check = false) {
    if (!dom || !(dom instanceof Element)) {
        throw new Error('Invalid DOM element');
    }

    const rect = dom.getBoundingClientRect();
    
    // Get the actual scroll positions
    const docScrollLeft = window.pageXOffset;
    const docScrollTop = window.pageYOffset;
    
    // Adjust coordinates for document scroll
    const adjustedX = x + docScrollLeft;
    const adjustedY = y + docScrollTop;
    
    // Precise boundary check considering document scroll
    const elementLeft = rect.left + docScrollLeft;
    const elementRight = rect.right + docScrollLeft;
    const elementTop = rect.top + docScrollTop;
    const elementBottom = rect.bottom + docScrollTop;
    
    const isOutsideX = adjustedX < elementLeft || adjustedX > elementRight;
    const isOutsideY = adjustedY < elementTop || adjustedY > elementBottom;
    
    if (isOutsideX || isOutsideY) {
        return { x: -1, y: -1 };
    }
    
    // Calculate relative position from element's top-left corner
    let relativeX = adjustedX - elementLeft;
    let relativeY = adjustedY - elementTop;
    
    // Account for element's own scroll
    relativeX += dom.scrollLeft;
    relativeY += dom.scrollTop;
    
    if (test && check){
        test = false
        const data = {
            rect: rect,
            docScrollLeft: docScrollLeft,
            docScrollTop: docScrollTop,
            x: x,
            y: y,
            width: window.innerWidth,
            height: window.innerHeight
        }

        console.log(JSON.stringify(data,null,2))
    }

    // Round to avoid floating point issues
    return {
        x: Math.round(relativeX * 100) / 100,
        y: Math.round(relativeY * 100) / 100
    };
}

window.resetTest = async function () {
    test = true
};

// ========== TEST CODE START ==========

let testOverlayActive = false;
let gazeDot = null;
let mouseDot = null;
let infoPanel = null;

function createTrackingDots() {
    if (!gazeDot) {
        gazeDot = document.createElement('div');
        gazeDot.id = 'test-gaze-dot';
        gazeDot.style.cssText = `
            position: fixed;
            width: 16px;
            height: 16px;
            background: rgba(255, 0, 0, 0.7);
            border: 3px solid white;
            border-radius: 50%;
            pointer-events: none;
            z-index: 999999;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.8);
            display: none;
            transform: translate(-50%, -50%);
        `;
        document.body.appendChild(gazeDot);
    }

    if (!mouseDot) {
        mouseDot = document.createElement('div');
        mouseDot.id = 'test-mouse-dot';
        mouseDot.style.cssText = `
            position: fixed;
            width: 12px;
            height: 12px;
            background: rgba(0, 255, 0, 0.7);
            border: 2px solid white;
            border-radius: 50%;
            pointer-events: none;
            z-index: 999998;
            box-shadow: 0 0 8px rgba(0, 255, 0, 0.8);
            display: none;
            transform: translate(-50%, -50%);
        `;
        document.body.appendChild(mouseDot);
    }

    if (!infoPanel) {
        infoPanel = document.createElement('div');
        infoPanel.id = 'test-info-panel';
        infoPanel.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.9);
            color: #00ff00;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            padding: 15px;
            border-radius: 8px;
            z-index: 1000000;
            min-width: 350px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            border: 2px solid #00ff00;
        `;
        infoPanel.innerHTML = `
            <div style="font-size: 14px; font-weight: bold; margin-bottom: 10px; color: #ffff00;">
                🎯 Relative.js Test Mode
            </div>
            <div style="margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #333;">
                <span style="color: #ff0000;">●</span> <strong>GAZE (Red)</strong> | 
                <span style="color: #00ff00;">●</span> <strong>MOUSE (Green)</strong>
            </div>
            <div id="test-gaze-info" style="margin-bottom: 10px; padding: 8px; background: rgba(255, 0, 0, 0.1); border-radius: 4px;">
                <div style="color: #ff6666; font-weight: bold;">GAZE:</div>
                <div>Client: <span id="gaze-client-x">-</span>, <span id="gaze-client-y">-</span></div>
                <div>Dom1 Rel: <span id="gaze-rel-x1">-</span>, <span id="gaze-rel-y1">-</span></div>
                <div>Dom2 Rel: <span id="gaze-rel-x2">-</span>, <span id="gaze-rel-y2">-</span></div>
            </div>
            <div id="test-mouse-info" style="margin-bottom: 10px; padding: 8px; background: rgba(0, 255, 0, 0.1); border-radius: 4px;">
                <div style="color: #66ff66; font-weight: bold;">MOUSE:</div>
                <div>Client: <span id="mouse-client-x">-</span>, <span id="mouse-client-y">-</span></div>
                <div>Dom1 Rel: <span id="mouse-rel-x1">-</span>, <span id="mouse-rel-y1">-</span></div>
                <div>Dom2 Rel: <span id="mouse-rel-x2">-</span>, <span id="mouse-rel-y2">-</span></div>
            </div>
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #333;">
                <button id="toggle-test-btn" style="
                    background: #ff4444;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: bold;
                    width: 100%;
                    font-family: inherit;
                ">STOP TEST</button>
            </div>
            <div style="margin-top: 8px; font-size: 10px; color: #888;">
                Console: toggleRelativeTest() to toggle
            </div>
        `;
        document.body.appendChild(infoPanel);

        document.getElementById('toggle-test-btn').addEventListener('click', () => {
            window.toggleRelativeTest();
        });
    }
}

window.updateTestGaze = function(clientX, clientY, dom1, dom2) {
    if (!testOverlayActive) return;
    
    try {
        if (!gazeDot || !infoPanel) {
            createTrackingDots();
        }

        if (gazeDot && clientX >= 0 && clientY >= 0) {
            gazeDot.style.display = 'block';
            gazeDot.style.left = clientX + 'px';
            gazeDot.style.top = clientY + 'px';

            const elemX = document.getElementById('gaze-client-x');
            const elemY = document.getElementById('gaze-client-y');
            const elemX1 = document.getElementById('gaze-rel-x1');
            const elemY1 = document.getElementById('gaze-rel-y1');
            const elemX2 = document.getElementById('gaze-rel-x2');
            const elemY2 = document.getElementById('gaze-rel-y2');
            
            if (elemX) elemX.textContent = clientX.toFixed(1);
            if (elemY) elemY.textContent = clientY.toFixed(1);

            if (dom1 && elemX1 && elemY1) {
                const rel1 = relativelyVar(clientX, clientY, dom1);
                elemX1.textContent = rel1.x.toFixed(1);
                elemY1.textContent = rel1.y.toFixed(1);
                elemX1.style.color = rel1.x === -1 ? '#ff4444' : '#00ff00';
                elemY1.style.color = rel1.y === -1 ? '#ff4444' : '#00ff00';
            }

            if (dom2 && elemX2 && elemY2) {
                const rel2 = relativelyVar(clientX, clientY, dom2);
                elemX2.textContent = rel2.x.toFixed(1);
                elemY2.textContent = rel2.y.toFixed(1);
                elemX2.style.color = rel2.x === -1 ? '#ff4444' : '#00ff00';
                elemY2.style.color = rel2.y === -1 ? '#ff4444' : '#00ff00';
            }
        }
    } catch (error) {
        console.error('updateTestGaze error:', error);
    }
};

window.updateTestMouse = function(clientX, clientY, dom1, dom2) {
    if (!testOverlayActive) return;
    
    try {
        if (!mouseDot || !infoPanel) {
            createTrackingDots();
        }

        if (mouseDot && clientX >= 0 && clientY >= 0) {
            mouseDot.style.display = 'block';
            mouseDot.style.left = clientX + 'px';
            mouseDot.style.top = clientY + 'px';

            const elemX = document.getElementById('mouse-client-x');
            const elemY = document.getElementById('mouse-client-y');
            const elemX1 = document.getElementById('mouse-rel-x1');
            const elemY1 = document.getElementById('mouse-rel-y1');
            const elemX2 = document.getElementById('mouse-rel-x2');
            const elemY2 = document.getElementById('mouse-rel-y2');
            
            if (elemX) elemX.textContent = clientX.toFixed(1);
            if (elemY) elemY.textContent = clientY.toFixed(1);

            if (dom1 && elemX1 && elemY1) {
                const rel1 = relativelyVar(clientX, clientY, dom1);
                elemX1.textContent = rel1.x.toFixed(1);
                elemY1.textContent = rel1.y.toFixed(1);
                elemX1.style.color = rel1.x === -1 ? '#ff4444' : '#00ff00';
                elemY1.style.color = rel1.y === -1 ? '#ff4444' : '#00ff00';
            }

            if (dom2 && elemX2 && elemY2) {
                const rel2 = relativelyVar(clientX, clientY, dom2);
                elemX2.textContent = rel2.x.toFixed(1);
                elemY2.textContent = rel2.y.toFixed(1);
                elemX2.style.color = rel2.x === -1 ? '#ff4444' : '#00ff00';
                elemY2.style.color = rel2.y === -1 ? '#ff4444' : '#00ff00';
            }
        }
    } catch (error) {
        console.error('updateTestMouse error:', error);
    }
};

window.toggleRelativeTest = function() {
    testOverlayActive = !testOverlayActive;

    if (testOverlayActive) {
        createTrackingDots();
        if (gazeDot) gazeDot.style.display = 'block';
        if (mouseDot) mouseDot.style.display = 'block';
        if (infoPanel) infoPanel.style.display = 'block';
        
        const btn = document.getElementById('toggle-test-btn');
        if (btn) {
            btn.textContent = 'STOP TEST';
            btn.style.background = '#ff4444';
        }
        
        console.log('%c✅ TEST MODE ACTIVE', 'color: #00ff00; font-size: 14px; font-weight: bold;');
        console.log('Red dot = GAZE | Green dot = MOUSE');
        console.log('Waiting for eye tracking data...');
        console.log('Make sure webgazer is running on the page');
    } else {
        if (gazeDot) gazeDot.style.display = 'none';
        if (mouseDot) mouseDot.style.display = 'none';
        if (infoPanel) infoPanel.style.display = 'none';
        console.log('%c⏹️ TEST MODE STOPPED', 'color: #ff4444; font-size: 14px; font-weight: bold;');
    }

    return testOverlayActive;
};

window.removeRelativeTest = function() {
    if (gazeDot) gazeDot.remove();
    if (mouseDot) mouseDot.remove();
    if (infoPanel) infoPanel.remove();
    gazeDot = null;
    mouseDot = null;
    infoPanel = null;
    testOverlayActive = false;
    console.log('Test overlay removed');
};

window.testRelativeDisplay = function() {
    console.log('Testing display with dummy data...');
    
    if (!testOverlayActive) {
        toggleRelativeTest();
    }
    
    const testX = 500;
    const testY = 300;
    
    const dom1 = document.getElementById('response-1') || document.querySelector('[id*="response"]') || document.body;
    const dom2 = document.getElementById('response-2') || document.querySelector('[id*="response"]:nth-of-type(2)') || document.body;
    
    console.log('Test coordinates:', testX, testY);
    console.log('Dom1:', dom1?.id || 'not found');
    console.log('Dom2:', dom2?.id || 'not found');
    
    if (window.updateTestGaze) {
        window.updateTestGaze(testX, testY, dom1, dom2);
        console.log('✓ Called updateTestGaze');
    }
    
    if (window.updateTestMouse) {
        window.updateTestMouse(testX + 20, testY + 20, dom1, dom2);
        console.log('✓ Called updateTestMouse');
    }
    
    console.log('Check if dots and panel are visible with data now');
};

console.log('%c📍 Relative.js Test Available', 'color: #00ffff; font-size: 14px; font-weight: bold;');
console.log('Commands:');
console.log('  toggleRelativeTest() - Start/stop test mode');
console.log('  testRelativeDisplay() - Test with dummy data to verify display');
console.log('  removeRelativeTest() - Remove all test elements');

// ========== TEST CODE END ==========