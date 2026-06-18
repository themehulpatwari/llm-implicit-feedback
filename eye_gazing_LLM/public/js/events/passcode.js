import { postRequest } from "../functions/requests.js";
// import { llm_redirect } from "../functions/redirect.js";

const form = document.getElementById('finished');
const task_array = JSON.parse(sessionStorage.getItem("task_array"));
const task_index = parseInt(sessionStorage.getItem("task_index"), 10);

window.addEventListener('load', async (e)=>{
    e.preventDefault();

    const token = document.getElementById('csrf_token').getAttribute('content');
    // const url = '/src/llm/nextTask.php?next=true';
    // const response = await getRequest(url, token);

    // const task_id = response.error ? -1 : response.response.task_id;
    // if(task_index + 1 >= task_array.length){
    //     document.getElementById('finished').style.display = 'none';
    //     return;
    // }

    const task_id = task_array[task_index];
    // const task_id = 80;

    const url = '/src/database/encrypt.php';
    const passcodeResponse = await postRequest(
        url, 
        JSON.stringify({
            task_id: task_id
        }), 
        token
    );
        
    const passcode = passcodeResponse.passcode;
    // console.log(passcodeResponse);
    document.getElementById('passcode').textContent = passcode;
    // document.getElementById("task_id_value").value = task_id;
    // document.getElementById("task_id_form").submit();
})

form.addEventListener('submit', async (e) =>{
    e.preventDefault();
    
    // Get the CSRF token for the request
    const token = document.getElementById('csrf_token').getAttribute('content');
    
    // Fetch the task count from the backend
    const taskCountUrl = '/src/database/task_count.php';
    const taskCountResponse = (taskCountUrl, token);
    const taskCount = taskCountResponse.task_count;
    console.log(taskCount);
    
    sessionStorage.setItem("task_index", task_index + 1);
    const task_id = task_array[task_index+1];
    console.log(task_id);
    console.log(taskCount);
    console.log(task_index)
    
    // Check task count before redirecting
    const MAX_TASKS = 50; // Set your maximum task threshold here
    
    if (taskCount >= MAX_TASKS) {
        // Redirect to completion page if tasks exceed threshold
        window.location.href = '/public/webpage/finished_batch.php';
    } else {
        // Check if this is the last task
        if (task_index + 1 >= task_array.length) {
            // Redirect to login if this is the last task
            window.location.href = '/public/webpage/login.php';
        } else {
            // Proceed with normal redirection based on task_id
            if(task_id % 2 === 0){
                window.location.href = '/public/webpage/pointwise.php';
            } else {
                window.location.href = '/public/webpage/pairwise.php';
            }
        }
    }
})