import {getRequest} from '../functions/requests.js';

const form = document.getElementById('consentForm');

// const form = document.querySelector('.form');
// console.log(form);

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    if('checkbox' in data){
        // document.getElementById('consentForm').style.display = 'none';
        // document.getElementById('consentID').style.display = 'none';
        // document.getElementById('nextPageID').style.display = 'block';

        const token = document.getElementById('csrf_token').getAttribute('content');
        const res = await getRequest('/src/database/record.php?checkbox=on', token);
        
        window.location.href = '/public/webpage/questionnaire.php';
    }
});