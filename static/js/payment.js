document.getElementById('pay-btn').addEventListener('click', function () {
    const options = {
        method: 'POST',
        headers: {
            accept: 'application/json',
            'content-type': 'application/json',
            authorization: 'Basic c2tfdGVzdF9uUnVobmFFMk1uZFYyNzhrbXJzaExGdEY6'
        },
        body: JSON.stringify({
            data: {
                attributes: {
                    amount: 129900, // Amount in cents (or smallest currency unit)
                    description: 'Standard Room',
                    remarks: 'Thank you for Booking!'
                }
            }
        })
    };

    fetch('https://api.paymongo.com/v1/links', options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            // Handle successful payment link creation here
            // You can redirect the user to the payment link or show it in a modal
        })
        .catch(err => console.error('Error:', err));
});