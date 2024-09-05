// checkout.js

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateShippingAddress() {
    console.log('updateShippingAddress function called');

    const recipientName = document.getElementById('recipient_name').value;
    const address = document.getElementById('full_address').value;
    const city = document.getElementById('city').value;
    const zipCode = document.getElementById('zip_code').value;
    const country = document.getElementById('country').value;

    console.log('Recipient Name:', recipientName);
    console.log('Address:', address);
    console.log('City:', city);
    console.log('Zip Code:', zipCode);
    console.log('Country:', country);

    if (!recipientName || !address || !city || !zipCode || !country) {
        alert('All fields are required');
        return;
    }

    const shippingData = JSON.stringify({
        recipient_name: recipientName,
        address: address,
        city: city,
        zip_code: zipCode,
        country: country
    });

    console.log('Shipping Data:', shippingData);

    fetch('/edit-shipping-address/', {
        method: 'POST',
        body: shippingData,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        window.location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function handlePayment(event) {
    const paymentMethod = document.getElementById('payment_method').value;
    if (paymentMethod === "1") {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Please select a payment method.',
        });
        event.preventDefault(); 
        return false; 
    }

    // Change the form action based on the selected payment method
    const form = document.getElementById('paymentForm');
    if (paymentMethod === 'paypal') {
        form.action = '/payment/';
    } else if (paymentMethod === 'credit_card') {
        form.action = '/credit_card/';
    } else if (paymentMethod === 'transfer') {
        form.action = '/transfer/';
    }
}

function initializeEventListeners() {
    console.log("Initializing event listeners"); 

    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(event) {
            handlePayment(event);
        });
    } else {
        console.log('Payment form not found');
    }

    const saveAddressButton = document.getElementById('saveAddressButton');
    if (saveAddressButton) {
        console.log('Save Address button found');
        saveAddressButton.addEventListener('click', function() {
            console.log('Save Address button clicked');
            updateShippingAddress();
        });
    } else {
        console.log('Save Address button not found, probably because a shipping address already exists.');
    }
}

export function initPage() {
    console.log("Initializing Checkout Page"); 
    initializeEventListeners();
}

document.addEventListener('DOMContentLoaded', initPage);
























