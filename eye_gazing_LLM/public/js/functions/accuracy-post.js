import { postRequest } from './requests.js';

document.addEventListener('beforeAccuracyPost', async (event) => {
    const { accuracy, token } = event.detail;
    
    sessionStorage.setItem('accuracy', accuracy);

    // try {
    //     const url = '/src/database/accuracy.php';
    //     const response = await postRequest(
    //         url,
    //         JSON.stringify({ accuracy }),
    //         token
    //     );
        
    //     console.log('Accuracy posted successfully:', response);
        
    // } catch (error) {
    //     console.error('Error posting accuracy:', error);
    // }
});