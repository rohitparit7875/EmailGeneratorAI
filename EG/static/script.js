document.getElementById('emailForm').addEventListener('submit', function(event) {
    // Prevent the page from reloading
    event.preventDefault(); 
    
    const form = event.target;
    // Collect data from the form fields
    const formData = {
        recipient: form.recipient.value,
        emailType: form.emailType.value,
        keywords: form.keywords.value
    };

    // Prepare UI for generation
    const generatedEmailDiv = document.getElementById('generatedEmail');
    
    // Show a loading message immediately inside the visible box
    generatedEmailDiv.innerHTML = 'Generating... Please wait.';

    // Send the data to the Flask backend's /generate route
    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        // Display the generated email from the backend response
        const emailContent = data.email; 
        generatedEmailDiv.innerHTML = emailContent.replace(/\n/g, '<br>'); 
    })
    .catch((error) => {
        console.error('Error:', error);
        generatedEmailDiv.innerHTML = 'An error occurred during generation. Check the server terminal.';
    });
});
// (The copyEmail function remains the same)