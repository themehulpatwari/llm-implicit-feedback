const east_coast = window.innerWidth;
const west_coast = window.innerHeight;
const percentConvert = (percent, width) =>{
    return (width === 'w' || width === true || width === 'width') ? (percent / 100) * east_coast : (percent / 100) * west_coast;
}

const positions = [
    {x: percentConvert(3, true), y: percentConvert(5, false)},
    {x: percentConvert(50, true), y: percentConvert(5, false)},
    {x: percentConvert(97, true), y: percentConvert(5, false)},
    {x: percentConvert(97, true), y: percentConvert(50, false)},
    {x: percentConvert(97, true), y: percentConvert(95, false)},
    {x: percentConvert(50, true), y: percentConvert(95, false)},
    {x: percentConvert(3, true), y: percentConvert(95, false)},
    {x: percentConvert(3, true), y: percentConvert(50, false)},
    {x: percentConvert(50, true), y: percentConvert(50, false)}
];

var index = 0;
var shmovement = false;

export function calibrationInit() {
    const vid = document.getElementById('webgazerVideoContainer');
    vid.style.top = `${.5 * window.innerHeight}px`;
    vid.style.left = `0px`;
    vid.style.transition = `top 1.0s cubic-bezier(0.47, 0, 0.745, 0.715), left 1.0s cubic-bezier(0.47, 0, 0.745, 0.715)`;
    
    const kdot = document.getElementById('kdot');
    kdot.style.display = 'block';
    kdot.style.top = `${positions[0].y}px`;
    kdot.style.left = `${positions[0].x}px`;
    
    kdot.addEventListener('click', (e) =>{
        if(shmovement) return;
        
        shmovement = true;
        e.preventDefault();
        
        // index = (index + 1) % positions.length;
        // console.log(index);
        if(++index >= positions.length){
            const token = document.getElementById('csrf_token').getAttribute('content');
            // console.log(document.getElementById('csrf_token'));
            // console.log(token);
            llm_redirect(token);
            return;
            // window.location.href = '/public/webpage/llm.php';
        } else if(index != 0){
            vid.style.top = `0px`;
            vid.style.left = `0px`;
        } else {
            vid.style.top = `${.5 * window.innerHeight}px`;
            vid.style.left = `0px`;
        }

        kdot.style.transition = `top 1.0s cubic-bezier(0.47, 0, 0.745, 0.715), left 1.0s cubic-bezier(0.47, 0, 0.745, 0.715)`;
        kdot.style.top = `${positions[index].y}px`;
        kdot.style.left = `${positions[index].x}px`;

        setTimeout(() => {
            shmovement = false;
        }, 1000)
    })
}