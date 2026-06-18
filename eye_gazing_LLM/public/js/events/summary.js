const form = document.getElementById('summary-form');

form.addEventListener('submit', (e) =>{
    e.preventDefault();

    const summary = form.elements['summary'].value.trim();
    console.log(summary)
    
    if (!summary) {
        alert('Summary cannot be empty. Please write a summary before submitting.');
        return;
    }

    sessionStorage.setItem('summary', summary);
    window.location.href = '/public/webpage/more.php';
})