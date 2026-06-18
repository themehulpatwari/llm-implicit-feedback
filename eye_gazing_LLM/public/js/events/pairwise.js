import {getRequest, postRequest} from '../functions/requests.js';
import * as queryCount from '../functions/queried.js';
import { validate_likerts, likert_values, post_likerts } from '../functions/likert.js';
import { getCurrentTimestampUTC } from '../functions/stopwatch.js';

const searchForm = document.getElementById('searchForm');
const task_array = JSON.parse(sessionStorage.getItem("task_array"));
const task_index = parseInt(sessionStorage.getItem("task_index"), 10);
// const task_array = [1]
// const task_index = 0

// window.onload = () =>{
//     task_array = JSON.parse(sessionStorage.getItem("task_array"));
//     task_index = parseInt(sessionStorage.getItem("task_index"), 10);
// };

searchForm.addEventListener('keydown', (e) =>{
    // const map = Object.fromEntries(new FormData(searchForm))
    // queryCount.increment();
    
    if(e.key ==='Enter' && !searchForm.elements['query'].value){
        e.preventDefault();
        searchForm.submit();
    }
});

searchForm.addEventListener('submit', async (e) =>{
    e.preventDefault();

    const token = document.getElementById('csrf_token').getAttribute('content');
    const query = searchForm.elements['query'].value;
    const task_id = task_array[task_index];
    // const task_id = 1;
    
    if(!query){
        alert("Please enter a question");
        return;
    }
    
    let url = '/src/database/task.php';
    if(!queryCount.get()){
        sessionStorage.setItem('query', query);
        // console.log("we sending it");
        // const accuracy = 0;
        const accuracy = parseFloat(sessionStorage.getItem('accuracy')) || 0;

        await postRequest(
            url,
            JSON.stringify({
                task_id : task_id,
                accuracy: accuracy
            }),
            token
        );
        // console.log("we sent it");
    } else if(!validate_likerts()) {
        alert("Please complete all rating options before submitting.");
        return;
    }

    if(queryCount.get() >= 0){
        const likert_element = document.getElementById('likert-scale-id');
        likert_element.style.visibility = 'visible';

        const question_text = document.getElementById('questions-text');
        question_text.style.visibility = 'visible';

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
            pairwise: true
        }), 
        token
    ); //error test 
    console.log(apiResponse);

    const adjustment = apiResponse.wasPromptAdjusted;

    let llmResponse1 = apiResponse.conversation[0];
    let llmResponse2 = apiResponse.conversation[1];

    // console.log(llmResponse1)
    // console.log(llmResponse2)

    llmResponse1.content = llmResponse1.content.trim().replace(/\n\s*\n/g, '\n');
    llmResponse2.content = llmResponse2.content.trim().replace(/\n\s*\n/g, '\n');


    document.getElementById('llm-response-1').textContent =  llmResponse1.content;
    document.getElementById('llm-response-2').textContent = llmResponse2.content;

    //.replace(/\r?\n/g, '')
      
    document.querySelector('input[name="query"]').placeholder = query;
    
    //add .model later
    if(!queryCount.get()){
        sessionStorage.setItem('llmResponse1', llmResponse1.content);
        sessionStorage.setItem('llmResponse2', llmResponse2.content);
        queryCount.increment();
    } else {
        //reservoir sampling
        if(Math.random() < (1/queryCount.increment())){
            sessionStorage.setItem('query', query);
            sessionStorage.setItem('llmResponse1', llmResponse1.content);
            sessionStorage.setItem('llmResponse2', llmResponse2.content);
        }
    }

    // const likertObj = likert_values();
    
    // console.log("we sending it");
    // url = '/src/database/conversation.php';
    // const response = await postRequest(
        //     url, 
        //     JSON.stringify({
            //         task_id: task_id,
            //         query: query,
            //         llm_response_1: llmResponse1.content,
            //         llm_response_2: llmResponse2.content,
            //         llm_name_1: llmResponse1.model,
            //         llm_name_2: llmResponse2.model,
            //         likert_1: likertObj.likertResponse1,
            //         likert_2: likertObj.likertResponse2,
            //         preference: likertObj.preferredResponse,
            //         adjustment: adjustment,
            //         timestamp: timestamp            
            //     }),
            //     token
            // );
    url = '/src/database/conversation.php';
    const timestamp = getCurrentTimestampUTC();
    const response = await postRequest(
        url, 
        JSON.stringify({
            task_id: task_id,
            query: query,
            llm_response_1: llmResponse1.content,
            llm_response_2: llmResponse2.content,
            llm_name_1: llmResponse1.model,
            llm_name_2: llmResponse2.model,
            adjustment: adjustment,
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
}

