import { postRequest } from "../functions/requests.js";

const form = document.getElementById("questionnaire-form");

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const err = document.getElementById('warning');

    const token = document.getElementById('csrf_token').getAttribute('content');
    const age = parseInt(form.elements['age'].value);
    if(age < 18 || age > 122){
        err.children[0].innerHTML = `The age inputted must be between 18-122. Please try again.`;
        err.style.display = 'block';
        return;
    }
    const location = form.elements['location'].value;
    const selected_education = form.elements['education'].value;

    const selected_race = Array.from(form.elements['race']).filter(option => option.checked).map(option => {
        if (option.value === "Other") {
            return form.elements['other_race'].value.trim() || "Other";
        }
        return option.value;
    });
    
    const total_length = selected_race.reduce((sum, cur) => sum += cur.length, 0);

    if(total_length > 256){
        const err = document.getElementById('warning');
        err.children[0].innerHTML = `Please reduce the number of charecters`;
        err.style.display = 'block';
        return;
    }

    if(selected_race.length === 0){
        err.children[0].innerHTML = `Please select one of the options for "Race:". If needed, pleaes use the "Other" option to better identify yourself.`;
        err.style.display = 'block';
        return;
    }

    let selected_gender = form.elements['gender'].value;
    if (selected_gender === 'Other'){
        selected_gender = form.elements['other_gender'].value
    }

    const url = '/src/database/responses.php';

    // console.log(`{token: ${token}}`);

    const res = await postRequest(url, 
        JSON.stringify({
            age: age,
            location: location,
            education: selected_education,
            race: selected_race,
            gender: selected_gender
        }),
        token
    );
    // console.log(res);

    if(res.status === 'success'){
        window.location.href = '/public/webpage/instruction.php';
    } else {
        const err = document.getElementById('warning');
        err.children[0].innerHTML = `Error: ${res.message}`;
        err.style.display = 'block';
    }
});
