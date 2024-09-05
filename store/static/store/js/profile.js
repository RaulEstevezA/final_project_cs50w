// profile.html

export function initPage() {
    console.log("Initializing Profile Page");

    document.getElementById('updateAccountInfoBtn').addEventListener('click', function(e) {
        e.preventDefault(); 
        updateAccountInfo(); 
    });

    document.getElementById('addAddressBtn').addEventListener('click', function(e) {
        e.preventDefault(); 
        document.getElementById('newAddressForm').style.display = 'block';
    });

    document.getElementById('saveNewAddressBtn').addEventListener('click', function(e) {
        e.preventDefault(); 
        updateShippingAddress(); 
    });

    document.getElementById('changePasswordBtn').addEventListener('click', function(e) {
        e.preventDefault();
        changePassword();
    });
}


function updateAccountInfo() {
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    const accountData = JSON.stringify({
        email: email,
        phone: phone,
        confirm_password: confirmPassword
    });

    fetch('/update_account_info/', {
        method: 'POST',
        body: accountData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error('Error:', data.error);
        } else {
            console.log('Account information updated successfully.');
            window.location.reload(); 
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


function updateShippingAddress() {
    const recipientName = document.getElementById('recipientNameInput').value;
    const address = document.getElementById('addressInput').value;
    const city = document.getElementById('cityInput').value;
    const zipCode = document.getElementById('zipCodeInput').value;
    const country = document.getElementById('countryInput').value;

    const shippingData = JSON.stringify({
        recipient_name: recipientName,
        address: address,
        city: city,
        zip_code: zipCode,
        country: country
    });

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
        console.log('Shipping address updated successfully.');
        window.location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


function changePassword() {
    const oldPassword = document.getElementById('oldPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmNewPassword = document.getElementById('confirmNewPassword').value;

    const passwordData = JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword,
        confirm_password: confirmNewPassword
    });

    fetch('/change_password/', {
        method: 'POST',
        body: passwordData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Password changed successfully.');
        window.location.reload(); 
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


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


