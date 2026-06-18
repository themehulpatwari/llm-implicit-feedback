const form = document.getElementById('finished');

form.addEventListener('submit', (e) =>{
    e.preventDefault();

    const understand_before = document.getElementsByName('understand-before').length > 0 ? parseInt(document.querySelector("input[name='understand-before']:checked").value) : null; 
    const understand_after = document.getElementsByName('understand-after').length > 0 ? parseInt(document.querySelector("input[name='understand-after']:checked").value) : null;

    if(understand_before === null || understand_after === null){
        return;
    }

    sessionStorage.setItem('understand_before', understand_before);
    sessionStorage.setItem('understand_after', understand_after);

    window.location.href = '/public/webpage/sentence.php';
});