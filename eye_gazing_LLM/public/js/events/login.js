import { postRequest, getRequest } from "../functions/requests.js";
import { checkBrowser } from '../functions/browser.js';

import task_json from '../../../config/task.json' with {type: 'json'};

checkBrowser();

const form = document.getElementById("login-form");

// Check task count immediately when page loads
(async function checkTaskCount() {
    const token = document.getElementById('csrf_token').getAttribute('content');
    // Fetch the task count from the backend
    const taskCountUrl = '/src/database/task_count.php';
    const taskCountResponse = await getRequest(taskCountUrl, token);
    const taskCount = taskCountResponse.error ? 0 : taskCountResponse.task_count;
    
    // Check task count before redirecting
    // const MAX_TASKS = 35; // Set your maximum task threshold here
    // if (taskCount >= MAX_TASKS) {
    //     window.location.href = '/public/webpage/finished_batch.php';
    //     return;
    // }
})();

window.onload = function () {
    json_loader();

    const container = document.getElementById('checkboxDropdown');
    const checkboxes = Array.from(container.querySelectorAll('label'));

    // Fisher-Yates Shuffle
    for (let i = checkboxes.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [checkboxes[i], checkboxes[j]] = [checkboxes[j], checkboxes[i]];
    }

    // Clear the container and append shuffled checkboxes
    container.innerHTML = '';
    checkboxes.forEach(label => container.appendChild(label));
};

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const token = document.getElementById('csrf_token').getAttribute('content');
    const user_id = form.elements['user_id'].value;
    // Send both value and label for each selected checkbox
    const tasks = Array.from(form.elements['options'])
        .filter(option => option.checked)
        .map(option => ({
            value: option.value,
            label: option.parentElement.textContent.trim()
        }));

    if(tasks.length === 0){
        const err = document.getElementById('login-warning');
        err.children[0].innerHTML = `You have not selected any of the tasks.`;
        err.style.display = 'block';
        return;
    }

    const url = '/src/database/auth.php';

    const res = await postRequest(url, 
        JSON.stringify({
            user_id: user_id,
            tasks: tasks
        }),
        token
    );
    // console.log(user_id, tasks, res);

    if(res.status === 'success'){
        // Store only the task IDs, not the full objects
        const taskIds = tasks.map(task => task.value);
        sessionStorage.setItem("task_array", JSON.stringify(taskIds));
        sessionStorage.setItem("task_index", 0);

        // const storedNumbers = JSON.parse(sessionStorage.getItem("myNumbers"));

        if(res.message === 'User ID saved to session and database' || res.message === 'User has not finished the questionnaire'){
            window.location.href = '/public/webpage/confirmation.php';
        } else {
            window.location.href = '/public/webpage/instruction.php';
        }
    } else {
        const err = document.getElementById('login-warning');
        
        if (res.message.includes("already done some of these tasks")) {
            err.children[0].innerHTML = `Mechanical Turk ID \"${user_id}\" has already completed some of these tasks.`;
        } else {
            err.children[0].innerHTML = `Please refresh the page and try again.`;
        }
        err.style.display = 'block';
    }
});


function json_loader(){
    const first_task_id = parseInt(task_json["first_task_id"], 10);
    const last_task_id = parseInt(task_json["last_task_id"], 10);

    const container = document.getElementById('checkboxDropdown');
    const topic_key_pairs = []

    for(let i = first_task_id; i <= last_task_id; i++) {
        topic_key_pairs.push({id: i, name:task_json.task_id[String(i)].article})
    }

    topic_key_pairs.forEach(topic_key_pairs => {
        const label = document.createElement("label");
        label.innerHTML = `<input type="checkbox" name="options" value="${topic_key_pairs.id}"> ${topic_key_pairs.name}`;
        container.appendChild(label);
    });
}