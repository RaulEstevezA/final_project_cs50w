// cart.js

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

export function initPage() {
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            const itemId = this.getAttribute('data-item-id');
            const newQuantity = this.value;
            const maxUnits = this.getAttribute('max');

            if (parseInt(newQuantity) > parseInt(maxUnits)) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: `You can only add up to ${maxUnits} units of this item.`
                });
                this.value = maxUnits;
                return;
            }

            fetch('/update_cart_item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ item_id: itemId, quantity: newQuantity })
            }).then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: data.error || 'Failed to update cart'
                        });
                    }
                });
        });
    });

    document.querySelectorAll('.btn-outline-danger').forEach(button => {
        button.addEventListener('click', function () {
            const itemId = this.getAttribute('data-item-id');

            Swal.fire({
                title: 'Are you sure?',
                text: "Do you want to remove this item from your cart?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, remove it!'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch('/remove_cart_item/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({ item_id: itemId })
                    }).then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                Swal.fire(
                                    'Removed!',
                                    'The item has been removed from your cart.',
                                    'success'
                                ).then(() => {
                                    window.location.reload();
                                });
                            } else {
                                Swal.fire('Failed to remove item', '', 'error');
                            }
                        });
                }
            });
        });
    });

    const clearCartButton = document.getElementById('clear-cart-button');
    if (clearCartButton && !clearCartButton.dataset.eventRegistered) {
        clearCartButton.dataset.eventRegistered = "true";
        clearCartButton.addEventListener('click', function () {
            Swal.fire({
                title: 'Are you sure?',
                text: "You won't be able to revert this!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, clear it!'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch('/clear_cart/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    }).then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                Swal.fire(
                                    'Cleared!',
                                    'Your cart has been cleared.',
                                    'success'
                                ).then(() => {
                                    window.location.reload();
                                });
                            } else {
                                Swal.fire('Failed to clear cart', '', 'error');
                            }
                        });
                }
            });
        });
    }
}





