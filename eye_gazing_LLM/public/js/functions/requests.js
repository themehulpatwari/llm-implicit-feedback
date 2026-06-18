async function handleResponse(response){
    try{
        if(!response.ok){throw {
            status: response.status,
            statusText: response.statusText
        }} 

        const content_type = response.headers.get('Content-Type');

        if(content_type && content_type.includes('text/plain')){
            return await response.text();
        } else if(content_type && content_type.includes('application/json')){
            return await response.json();
        } else{
            throw new Error(`Unsupported Response Content-Type: ${content_type}`);
        }
    } catch (error) {
        console.error(error);
        return {error: error};
    }
}

export async function getRequest(url, token) {
    // console.log('hi');
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            "Content-Type": 'text/plain',
            'X-CSRF-Token': token
        }
    })
    console.log(url);
    // if(url === '/src/database/auth.php'){
    // }

    return handleResponse(response);
}

export async function postRequest(url, data, token) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            "Content-Type": 'text/plain',
            'X-CSRF-Token': token
        },
        body: data
    })

    return handleResponse(response);
}