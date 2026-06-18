import {getRequest, postRequest} from '../functions/requests.js';
import * as queryCount from '../functions/queried.js';
import { validate_likerts, likert_values, post_likerts } from '../functions/likert.js';
import { getCurrentTimestampUTC } from '../functions/stopwatch.js';

const searchForm = document.getElementById('searchForm');
const task_array = JSON.parse(sessionStorage.getItem("task_array"));
const task_index = parseInt(sessionStorage.getItem("task_index"), 10);
// const task_array = [1]
// const task_index = 0

searchForm.addEventListener('keydown', (e) =>{
    // const map = Object.fromEntries(new FormData(searchForm))
    
    if(e.key ==='Enter' && !searchForm.elements['input1'].value){
        e.preventDefault();
        searchForm.submit();
    }
});

// Helper to show/hide and populate the comparison section
function showComparisonSection(prevAnswer, currAnswer) {
    const comparisonSection = document.getElementById('comparison-section');
    const prevDiv = document.getElementById('previous-answer');
    const currDiv = document.getElementById('current-answer');
    if (prevAnswer && currAnswer) {
        prevDiv.textContent = prevAnswer;
        currDiv.textContent = currAnswer;
        comparisonSection.style.display = 'block';
    } else {
        comparisonSection.style.display = 'none';
    }
}

// On page load, hide comparison section
document.addEventListener('DOMContentLoaded', () => {
    showComparisonSection(null, null);
});

searchForm.addEventListener('submit', async (e) =>{
    e.preventDefault();

    const token = document.getElementById('csrf_token').getAttribute('content');
    const query = searchForm.elements['query'].value;
    const task_id = task_array[task_index];

    if(!query){
        alert("Please enter a question");
        return;
    }
    
    let url = '/src/database/task.php';
    if(!queryCount.get()){
        sessionStorage.setItem('query', query);
        const accuracy = parseFloat(sessionStorage.getItem('accuracy')) || 0;
        await postRequest(
            url,
            JSON.stringify({
                task_id : task_id,
                accuracy: accuracy
            }),
            token
        );
    } else if(!validate_likerts()) {
        alert("Please complete all rating options before submitting.");
        return;
    }

    if(queryCount.get() >= 0){
        const likert_element = document.getElementById('likert-scale-id');
        likert_element.style.visibility = 'visible';
        const scrollInstruction = document.getElementById('scroll-instruction');
        scrollInstruction.style.visibility = 'visible';
    }

    if(queryCount.get() >= 1){
        post_likerts();
    }

    if(queryCount.get() >= 2){
        const element = document.getElementById('finished');
        element.style.visibility = 'visible';
        const scrollInstruction = document.getElementById('scroll-instruction');
        scrollInstruction.style.visibility = 'hidden';
    }

    searchForm.elements['query'].value = '';
    url = '/src/llm/apiCall.php';
    const apiResponse = await postRequest(
        url, 
        JSON.stringify({
            query: query,
            pairwise: false
        }), 
        token
    );
    // console.log(apiResponse)
    
    const adjustment = apiResponse.wasPromptAdjusted;
    
    let llmResponse1 = apiResponse.conversation[0];
    // console.log(llmResponse1);
    
    llmResponse1.content = llmResponse1.content.trim().replace(/\n\s*\n/g, '\n');
    
    document.getElementById('llm-response-1').textContent = llmResponse1.content;
    
    document.querySelector('input[name="query"]').placeholder = query;
    
    //add .model later
    if(!queryCount.get()){
        sessionStorage.setItem('llmResponse1', llmResponse1.content);
        sessionStorage.setItem('prevResponse', llmResponse1.content);

        queryCount.increment();
        // First question, no comparison
        showComparisonSection(null, null);
    } else {
        // Get the previous answer BEFORE updating sessionStorage
        const prevAnswer = sessionStorage.getItem('prevResponse');
        const currAnswer = llmResponse1.content;
        
        //reservoir sampling
        if(Math.random() < (1/queryCount.increment())){
            sessionStorage.setItem('query', query);
            sessionStorage.setItem('llmResponse1', llmResponse1.content);
        }
        
        // Show comparison section only after all validations are complete and API response is received
        if (prevAnswer && currAnswer && queryCount.get() > 1) {
            showComparisonSection(prevAnswer, currAnswer);
        }

        sessionStorage.setItem('prevResponse', llmResponse1.content);
        // sessionStorage.setItem('llmResponse1', llmResponse1.content)
    }
    
    // const likertObj = likert_values();
    // console.log(`{task_id: ${task_id}}`);
    
    url = '/src/database/conversation.php';
    const timestamp = getCurrentTimestampUTC();
    
    // Only get preference if this is not the first question
    let preference = null;
    if (queryCount.get() > 1) {
        const comparisonFeedback = document.getElementById("comparison-feedback");
        preference = comparisonFeedback ? comparisonFeedback.value : null;
        // Convert empty string to null
        if (preference === "") {
            preference = null;
        }
    }
    
    const response = await postRequest(
        url, 
        JSON.stringify({
            task_id: task_id,
            query: query,
            llm_response_1: llmResponse1.content,
            llm_response_2: null,
            llm_name_1: llmResponse1.model,
            llm_name_2: null,
            adjustment: adjustment,
            preference: preference,
            timestamp: timestamp
        }),
        token
    );

    sessionStorage.setItem('query_id', response.query_id);

    clearLikertScale();

    const responseContainers = document.querySelectorAll('.response-container');
    responseContainers.forEach(container => {
        container.scrollTop = 0;
    });
});



function clearLikertScale() {
    const radioButtons = document.querySelectorAll('.likert-scale input[type="radio"]');
    
    radioButtons.forEach(radio => {
        radio.checked = false;
    });
    
    // Clear comparison feedback as well
    const comparisonFeedback = document.getElementById('comparison-feedback');
    if (comparisonFeedback) {
        comparisonFeedback.value = '';
    }
}
