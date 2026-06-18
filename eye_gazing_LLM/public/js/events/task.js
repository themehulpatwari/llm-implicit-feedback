// import { getQueryBool, setQueryBool } from "./singlewise.js";
import * as queryCount from '../functions/queried.js';
import { postRequest, getRequest } from "../functions/requests.js";
import { llm_redirect } from "../functions/redirect.js";
// import { validateForm } from '/public/js/events/pairwise.js';
import { validate_likerts, post_likerts } from '../functions/likert.js';
import { getCurrentTimestampUTC } from '../functions/stopwatch.js';

import task_json from '../../../config/task.json' with {type: 'json'};

const task_array = JSON.parse(sessionStorage.getItem("task_array"));
const task_index = parseInt(sessionStorage.getItem("task_index"), 10);

window.addEventListener('load', (e) =>{
    e.preventDefault()

    const task_id = parseInt(task_array[task_index], 10);
    // const task_id = 208;
    // const switch_case = ((task_id - 30) % 60);
    switch_tasks(task_id);
});

document.getElementById('finished').addEventListener('submit', async (e) =>{
    e.preventDefault();

    // const temp = validate_likerts();
    // console.log(`validate_likerts() response: ${temp}`);

    if (!validate_likerts()) {
        alert("Please complete all rating options before submitting.");
        return;
    }

    if (queryCount.get() < 3){
        return;
    }
    queryCount.reset();

    window.resetConversation();

    await post_likerts();


    // const token = document.getElementById('csrf_token').getAttribute('content');
    
    // const url = '/src/database/complete.php';
    // const task_id =  parseInt(task_array[task_index], 10);

    // await postRequest(
    //     url, 
    //     JSON.stringify({
    //         task_id: task_id,
    //         timestamp: getCurrentTimestamp()           
    //     }),
    //     token
    // );

    sessionStorage.setItem('time', getCurrentTimestampUTC());

    window.location.href = '/public/webpage/summary.php';
});

window.resetConversation = async function () {
    let url = '/src/llm/reset_conversation.php';
    const token = document.getElementById('csrf_token').getAttribute('content');
    const response = await getRequest(url, token);
    // console.log(response);
};

function switch_tasks(task_id){
    const specific = document.getElementById('task-specific');    
    const child = specific.children[0];
    const topic = task_json.task_id?.[String(task_id)]?.article;

    if (topic !== undefined && topic !== null){
        child.innerHTML = `Please query about ${topic}`;
    } else {
        child.innerHTML = `An error has occured with the task_id. Please report to the study administrator.`;
    }
    specific.style.display = 'block';
}