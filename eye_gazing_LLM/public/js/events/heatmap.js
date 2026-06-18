let heatmapInstance;

const config = {
    radius: 25,
    maxOpacity: 0.5,
    minOpacity: 0,
    blur: 0.75
}

// Trimmed down version of webgazer's click listener since the built-in one isn't exported
// Needed so we can have just the click listener without the move listener
// (The move listener was creating a lot of drift)
async function clickListener(event) {
    webgazer.recordScreenPosition(event.clientX, event.clientY, 'click'); // eventType[0] === 'click'
}

export function setupHeatmap() {
    const height = window.innerHeight;
    const width = window.innerWidth;

    const container = document.createElement('div');
    container.id = 'heatmapContainer';
    container.style.height = `${height}px`;
    container.style.width = `${width}px`;

    document.getElementById('kdot').insertAdjacentElement('afterend', container);

    // Don't use mousemove listener
    webgazer.removeMouseEventListeners();
    // document.addEventListener('click', clickListener);

    // Set up the container
    // let container = document.getElementById('heatmapContainer');
    config.container = container;

    // create heatmap
    heatmapInstance = h337.create(config);
    container.style.position = 'absolute';
    container.style.zIndex = '0';

    // const canvas = document.getElementById('yourCanvasId');
    // canvas.getContext('2d', { willReadFrequently: true });
}

export function addData(point){
    heatmapInstance.addData(point);
}