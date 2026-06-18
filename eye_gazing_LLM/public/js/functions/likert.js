import * as queryCount from '../functions/queried.js';
import { postRequest } from './requests.js';

export function validate_likerts() {
    const likertResponse1 = queryCount.get() >= 1 ? document.querySelectorAll("input[name='response1-likert']:checked").length > 0 : true;
    const likertResponse2 = document.getElementsByName('response2-likert').length > 0 ? document.querySelectorAll("input[name='response2-likert']:checked").length > 0 : true; 
    const preferredResponse = document.getElementsByName('preferred-response').length > 0 ? document.querySelector("input[name='preferred-response']:checked") !== null : true;
    
    // Validate comparison feedback if comparison section is visible
    const comparisonSection = document.getElementById('comparison-section');
    const comparisonFeedback = comparisonSection && comparisonSection.style.display !== 'none' ? document.getElementById('comparison-feedback').value !== '' : true;
        // preferred-responsepreferred-response
    // console.log(likertResponse1, likertResponse2, preferredResponse, comparisonFeedback);
    return likertResponse1 && likertResponse2 && preferredResponse && comparisonFeedback;
}

export function likert_values(){
    if(!validate_likerts()){
        return {likertResponse1: null, likertResponse2: null, preferredResponse: null, comparisonFeedback: null};        
    }
    
    const likertResponse1 = document.querySelector('input[name="response1-likert"]:checked').value;

    const likertResponse2 = document.getElementsByName('response2-likert').length > 0 ? (document.querySelector('input[name="response2-likert"]:checked').value) : null; 
    const preferredResponse = document.getElementsByName('preferred-response').length > 0 ? (document.querySelector("input[name='preferred-response']:checked").value) : null;
    
    // Get comparison feedback if comparison section is visible
    const comparisonSection = document.getElementById('comparison-section');
    const comparisonFeedback = comparisonSection && comparisonSection.style.display !== 'none' ? 
        document.getElementById('comparison-feedback').value : null;

    // console.log("hi")
    return {likertResponse1: likertResponse1, likertResponse2: likertResponse2, preferredResponse: preferredResponse, comparisonFeedback: comparisonFeedback};
}

export async function post_likerts(){
    const token = document.getElementById('csrf_token').getAttribute('content');
    
    const likert_obj = likert_values();
    const query_id = sessionStorage.getItem('query_id');
    
    // Determine which preference value to use based on task type
    // For pointwise: use comparisonFeedback (dropdown comparing current vs previous)
    // For pairwise: use preferredResponse (radio buttons choosing between two responses)
    let preferenceValue = null;
    if (likert_obj.comparisonFeedback !== null) {
        // Pointwise task - use comparison feedback
        preferenceValue = likert_obj.comparisonFeedback;
    } else if (likert_obj.preferredResponse !== null) {
        // Pairwise task - use preferred response
        preferenceValue = likert_obj.preferredResponse;
    }
    
    console.log(likert_obj.likertResponse1, likert_obj.likertResponse2, likert_obj.preferredResponse, likert_obj.comparisonFeedback)
    const url = '/src/database/likertUpdate.php';
    await postRequest(
        url, 
        JSON.stringify({
            likert_1: likert_obj.likertResponse1,
            likert_2: likert_obj.likertResponse2,
            preference: preferenceValue,
            query_id: query_id
        }), 
        token
    );   
}

window.likert_values = likert_values;