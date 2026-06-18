//maybe put the first time condition here?
import { getRequest } from "./requests.js";

export async function llm_redirect(token){
    // console.log("function called");
    let url = '/src/llm/nextTask.php?next=false';
    const response = await getRequest(url, token);
    const task_id = response.error ? -1 : response.response.task_id;
    //error message for -1 is best
    // console.log(response)
    if(task_id % 2  === 0){
        window.location.href = '/public/webpage/pointwise.php';
    } else {
        window.location.href = '/public/webpage/pairwise.php';
    }
}

document.addEventListener("triggerRedirect", async (event) => {
    const { token } = event.detail; // Extract the token from the event
    await llm_redirect(token); // Call the function with the token
});