import { calibrationInit } from "../events/eye.js";
import { setupHeatmap, addData} from "../events/heatmap.js";
import { postRequest } from "../functions/requests.js";
import { settings } from "../config.js";
import { relativelyVar} from "../functions/relative.js";
import { getMouse } from "../functions/mouse.js";
import { detect_characters } from "../functions/character.js";
import * as queryCount from '../functions/queried.js';
import { getPageTime } from '../functions/pageTimer.js';

// Heatmap buffer
const buffer_size = 100

let lastTime = 0;
let lastGaze = {x: 0, y: 0};

let absolute_gaze_data_buffer = [];
let relative_gaze_data_buffer_one = [];
let relative_gaze_data_buffer_two = [];

let absolute_mouse_buffer = [];
let relative_mouse_buffer_one= [];
let relative_mouse_buffer_two = [];

const token = document.getElementById('csrf_token').getAttribute('content');

const task_array = JSON.parse(sessionStorage.getItem("task_array"));
const task_index = parseInt(sessionStorage.getItem("task_index"), 10);

function heatmapStuff(clock){
    // Init if lastTime not set
    if(!lastTime) {
        lastTime = clock;
    }

    // In this we want to track how long a point was being looked at,
    // so we need to buffer where the gaze moves to and then on next move
    // we calculate how long the gaze stayed there.
    if(!!lastGaze) {
        if(!!lastGaze.x && !!lastGaze.y) {
            let duration = clock-lastTime;
            let point = {
                x: Math.floor(lastGaze.x),
                y: Math.floor(lastGaze.y),
                value: duration
            }
            
            if(settings.h){
                addData(point);
            }
        }
    }
}

function camera_validate(){
    const camera_box = document.getElementById('webgazerFaceFeedbackBox');
    const style = window.getComputedStyle(camera_box);
    const color = style.getPropertyValue('border-top-color');
    const camera_validation = color === 'rgb(0, 128, 0)' ? 1 : 0;
    return camera_validation;
}

export async function pointwiseEyeListener(webgazer, data, clock) { // public/js/events/eye_listener.js
    // data is the gaze data, clock is the time since webgazer.begin()
    const task_id = task_array[task_index];

    if(!data){
        return;
    }

    // heatmapStuff(clock);
    const page_timer = getPageTime()
    const camera_validation = camera_validate();
    
    const gazeDataObj = {
        x: data.x === null ? -1: data.x,
        y: data.y === null ? -1: data.y,
        page_timer: page_timer, 
        epoch: Date.now()
    }
    
    absolute_gaze_data_buffer.push(gazeDataObj);
    
    const rel_gaze_obj = relativelyVar(gazeDataObj.x, gazeDataObj.y, document.getElementById('response-1'));

    const sliding_string_gaze = detect_characters(gazeDataObj.x, gazeDataObj.y, rel_gaze_obj.x, rel_gaze_obj.y);
    relative_gaze_data_buffer_one.push(
        {
            x: rel_gaze_obj.x, 
            y: rel_gaze_obj.y, 
            string: sliding_string_gaze.string, 
            index: sliding_string_gaze.index, 
            page_timer: page_timer, 
            validate: camera_validation,
            epoch: Date.now()
        }
    );

    // window.absoluteMouse.mousePush(clock);
    // window.relativeMouse.mousePush(clock);
    
    const mouse = getMouse();
    absolute_mouse_buffer.push({x: mouse.x, y: mouse.y, page_timer: page_timer, epoch: Date.now()});
    
    const rel_mouse_obj = relativelyVar(mouse.x, mouse.y, document.getElementById('response-1'));
    const sliding_string_mouse = detect_characters(mouse.x, mouse.y, rel_mouse_obj.x, rel_mouse_obj.y)
    relative_mouse_buffer_one.push(
        {
            x: rel_mouse_obj.x, 
            y: rel_mouse_obj.y, 
            string: sliding_string_mouse.string, 
            index: sliding_string_mouse.index, 
            page_timer: page_timer, 
            validate: camera_validation,
            epoch: Date.now()
        }
    );
    
    if(absolute_gaze_data_buffer.length >= buffer_size && queryCount.get() > 0){
        postRequest(
            '/src/database/single_behavior.php', 
            JSON.stringify({
                task_id: task_id,
                absolute_gaze_data: absolute_gaze_data_buffer,
                relative_gaze_data: relative_gaze_data_buffer_one, 
                absolute_mouse_data: absolute_mouse_buffer,
                relative_mouse_data: relative_mouse_buffer_one
            }), 
            token);
            
            absolute_gaze_data_buffer = [];
            absolute_mouse_buffer = [];
            relative_gaze_data_buffer_one = [];
            relative_mouse_buffer_one = [];
            // window.absoluteMouse.clearMouseData();
            // window.relativeMouse.clearMouseData();
        }
        
        lastGaze = data;
        lastTime = clock;
    }
    
    //we set the interval of time between each eyeListener to be some arbitrary time (e.g: 300ms)
    
export async function pairwiseEyeListener(webgazer, data, clock, dom1, dom2) { // (data,clock) => {pairwiseEyeListener(data,clock, [insert dom1], [insert dom2])}
    // data is the gaze data, clock is the time since webgazer.begin()
    const task_id = task_array[task_index];

    if(!data){
        return;
    }
    
    // heatmapStuff();
    const page_timer = getPageTime()
    const camera_validation = camera_validate();
    
    const gazeDataObj = {
        x: data.x === null ? -1 : data.x,
        y: data.y === null ? -1 : data.y,
        page_timer: page_timer, 
        epoch: Date.now()
    };

    const mouse = getMouse();
    absolute_gaze_data_buffer.push(gazeDataObj);
    absolute_mouse_buffer.push({x: mouse.x, y: mouse.y, page_timer: page_timer, epoch: Date.now()});
    
    // TEST START
    if (window.updateTestGaze && gazeDataObj.x >= 0 && gazeDataObj.y >= 0) {
        window.updateTestGaze(gazeDataObj.x, gazeDataObj.y, dom1, dom2);
    }
    if (window.updateTestMouse && mouse.x >= 0 && mouse.y >= 0) {
        window.updateTestMouse(mouse.x, mouse.y, dom1, dom2);
    }
    if (window.testOverlayActive === undefined) {
        window.testOverlayActive = false;
        console.log('Eye listener test hooks installed. Run toggleRelativeTest() to start.');
    }
    // TEST END
    
    // Relative gaze data for both windows
    const rel_gaze_obj_one = relativelyVar(gazeDataObj.x, gazeDataObj.y, dom1);
    const rel_gaze_obj_two = relativelyVar(gazeDataObj.x, gazeDataObj.y, dom2);
    const rel_mouse_obj_one = relativelyVar(mouse.x, mouse.y, dom1, true);
    const rel_mouse_obj_two = relativelyVar(mouse.x, mouse.y, dom2);
    
    const sliding_string_gaze_one = detect_characters(gazeDataObj.x, gazeDataObj.y, rel_gaze_obj_one.x, rel_gaze_obj_one.y);
    const sliding_string_gaze_two = detect_characters(gazeDataObj.x, gazeDataObj.y, rel_gaze_obj_two.x, rel_gaze_obj_two.y);
    const sliding_string_mouse_one = detect_characters(mouse.x, mouse.y, rel_mouse_obj_one.x, rel_mouse_obj_one.y);
    const sliding_string_mouse_two = detect_characters(mouse.x, mouse.y, rel_mouse_obj_two.x, rel_mouse_obj_two.y);
    
    relative_gaze_data_buffer_one.push(
        {
            x: rel_gaze_obj_one.x, 
            y: rel_gaze_obj_one.y, 
            string: sliding_string_gaze_one.string, 
            index: sliding_string_gaze_one.index, 
            page_timer: page_timer, 
            validate: camera_validation,
            epoch: Date.now()
        }
    );
    relative_gaze_data_buffer_two.push(
        {
            x: rel_gaze_obj_two.x, 
            y: rel_gaze_obj_two.y, 
            string: sliding_string_gaze_two.string, 
            index: sliding_string_gaze_two.index, 
            page_timer: page_timer, 
            validate: camera_validation,
            epoch: Date.now()
        }
    );
    relative_mouse_buffer_one.push(
        {
            x: rel_mouse_obj_one.x, 
            y: rel_mouse_obj_one.y, 
            string: sliding_string_mouse_one.string, 
            index: sliding_string_mouse_one.index, 
            page_timer: page_timer, 
            validate: camera_validation,
            epoch: Date.now()
        }
    );
    relative_mouse_buffer_two.push(
        {
            x: rel_mouse_obj_two.x, 
            y: rel_mouse_obj_two.y, 
            string: sliding_string_mouse_two.string, 
            index: sliding_string_mouse_two.index, 
            page_timer: page_timer, 
            validate: camera_validation,
            epoch: Date.now()
        }
    );
    
    // Post data to server when buffer reaches threshold (e.g., 10 entries)
    // console.log(`{task_id: ${task_id}}`);
    // console.log(task_id);
    if (absolute_gaze_data_buffer.length >= buffer_size && queryCount.get() > 0) {
        postRequest(
            '/src/database/pairwise_behavior.php',
            JSON.stringify({
                task_id: task_id,
                absolute_gaze_data: absolute_gaze_data_buffer,
                relative_gaze_data_left: relative_gaze_data_buffer_one,
                relative_gaze_data_right: relative_gaze_data_buffer_two,
                absolute_mouse_data: absolute_mouse_buffer,
                relative_mouse_data_left: relative_mouse_buffer_one,
                relative_mouse_data_right: relative_mouse_buffer_two,
            }),
            token
        );

        absolute_gaze_data_buffer = [];
        absolute_mouse_buffer = [];
        relative_gaze_data_buffer_one = [];
        relative_gaze_data_buffer_two = [];
        relative_mouse_buffer_one = [];
        relative_mouse_buffer_two = [];
        // window.absoluteMouse.clearMouseData();
        // window.relativeMouse.clearMouseData();
    }

    lastGaze = data;
    lastTime = clock;
}

