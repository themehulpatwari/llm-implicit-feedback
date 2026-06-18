import { postRequest, getRequest } from "../functions/requests.js";

const form = document.getElementById('feedback-form');

const task_array = JSON.parse(sessionStorage.getItem("task_array"));
const task_index = parseInt(sessionStorage.getItem("task_index"), 10);

window.addEventListener('load', (e)=>{
    e.preventDefault();

    const query = document.getElementById('query');
    const response = document.getElementById('response');
    query.innerHTML = sessionStorage.getItem('query');
    response.innerHTML = sessionStorage.getItem('llmResponse1'); // ADD LLMRESPONSE2?
});

form.addEventListener('submit', async (e) =>{
    e.preventDefault();

    const sentence = form.elements['sentence'].value;
    // const summary = form.elements['summary'].value
    const understand_before = sessionStorage.getItem('understand_before');
    const understand_after = sessionStorage.getItem('understand_after');
    const summary = sessionStorage.getItem('summary');
    const feedback = form.elements['feedback'].value;
    const query = sessionStorage.getItem('query');
    const llmResponse1 = sessionStorage.getItem('llmResponse1');

    const task_id = task_array[task_index];

    if(!sentence || !summary){
        return;
    }

    let url = '/src/database/feedback.php';
    const token = document.getElementById('csrf_token').getAttribute('content');
    
    await postRequest(url, 
        JSON.stringify({
            task_id: task_id,
            sentence: sentence,
            understand_before: understand_before,
            understand_after: understand_after,
            summary: summary,
            feedback: feedback,
            query: query,
            llm_response: llmResponse1,
            timestamp: sessionStorage.getItem('time')
        }),
        token
    );

    // Increment global task counter
    const counterUrl = '/src/database/task_counter.php';
    try {
        const counterResponse = await fetch(counterUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await counterResponse.json();
        console.log('Global task count updated:', data.count);
    } catch (error) {
        console.error('Error updating task count:', error);
    }

    // console.log('Feedback submitted:', {
    //     task_id: task_id,
    //     sentence: sentence,
    //     understand_before: understand_before,
    //     understand_after: understand_after,
    //     summary: summary,
    //     feedback: feedback
    // });

    // url = '/src/llm/nextTask.php?next=true';
    // await getRequest(url, token);

    
    window.location.href = '/public/webpage/passcode.php';
})