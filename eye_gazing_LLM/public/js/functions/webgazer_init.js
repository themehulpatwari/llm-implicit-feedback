import { calibrationInit } from "../events/eye.js";
import { setupHeatmap, addData} from "../events/heatmap.js";
import { postRequest } from "./requests.js";
import { settings } from "../config.js";
import { pointwiseEyeListener, pairwiseEyeListener} from "../events/eye_listener.js";

window.saveDataAcrossSessions = true;
// let { absoluteMouse, relativeMouse} = {absoluteMouse: ()=> {return;}, relativeMouse: ()=> {return;}}

const task_array = JSON.parse(sessionStorage.getItem("task_array"));
const task_index = parseInt(sessionStorage.getItem("task_index"), 10);

// window.addEventListener('load', ()=>{
//     const page_come_from = '';
//     if(page_come_from === 'login.php'){
//         element.href = 'login.php';
//         return;
//     }

//     const element = document.getElementById('task');

//     const task_id = task_array[task_index];
//     const url = task_id % 2 == 0 ? 'pairwise.php' : 'pointwise.php';
//     element.href = url;
// })

window.addEventListener('load', async(e) => {
    e.preventDefault();
    if(window.webgazer && settings.w){
        webgazer.setRegression('ridge')
            .showVideoPreview(true)
            // .removeMouseEventListeners()
            .begin()
            .then(async ()=>{
                if(settings.c){
                    calibrationInit();    
                } else{
                    // console.log("what abt here")
                    const module = await import("../events/vid_init.js"); 
                    module.vidInitLLM();
                }
            });

        if(settings.c){
            webgazer.showPredictionPoints(true);
        } else{
            webgazer.showPredictionPoints(false);
            // webgazer.showPredictionPoints(true);
        }

        if(settings.h){
            setupHeatmap();
        }

        // if(!settings.c){
        if(settings.c){
            // const timeoutObj = webgazerTimeout();

            if (settings.p) {
                console.log('here');
                // CAUSE OF ERROR: replace column-1 and column-2 with actual elements: llm-response-1 and llm-response-2
                webgazer.setGazeListener((data, elapsedTime) => pairwiseEyeListener(webgazer, data, elapsedTime, document.getElementById('llm-response-1'), document.getElementById('llm-response-2')));
            } else {
                webgazer.setGazeListener((data, elapsedTime) => pointwiseEyeListener(webgazer, data, elapsedTime));
            }
        }    
    }
});

window.BeforeUnloadEvent = () => {
    if (window.saveDataAcrossSessions) {
        webgazer.setGlobalData();
        webgazer.end();
    } else {
        localforage.clear();
    }
}; 

// let relative_gaze_data_buffer = [];
// let absolute_gaze_data_buffer_window1 = [];
// let relative_gaze_data_buffer_window1 = [];
// let absolute_gaze_data_buffer_window2 = [];
// let relative_gaze_data_buffer_window2 = [];

// window.addEventListener('blur', () =>{
//     webgazer.pause();
// });

// window.addEventListener('focus', () =>{
//     webgazer.resume();
// });

// function webgazerTimeout(){
//     let timer;
//     let seconds = 0;

//     function startTimer() {
//         timer = setInterval(() => {
//             seconds++;
//             console.log(`Timer: ${seconds} seconds`);
//         }, 1000);
//     }

//     window.addEventListener('focus', function() {
//         console.log('Page focused - resuming timer');
//         startTimer();
//     });

//     window.addEventListener('blur', function() {
//         console.log('Page blurred - pausing timer');
//         clearInterval(timer);
//     });

//     startTimer();
// }