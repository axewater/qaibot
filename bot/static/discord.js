function performReadback(serverId, button) {
    const spinner = button.nextElementSibling;
    button.disabled = true;
    spinner.style.display = 'inline-block';

    console.log('Performing readback on server:', serverId);
    fetch(`/perform_readback/${serverId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        // You can display a success message or update the UI accordingly
        button.disabled = false;
        spinner.style.display = 'none';
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle any errors that occurred during the request
        button.disabled = false;
        spinner.style.display = 'none';
    });
}