/* product_view.js */

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
    const thumbnails = document.querySelectorAll('.product-view-thumbnail');
    const mainImage = document.querySelector('.main-image');
    const prevButton = document.querySelector('.product-view-prev-button');
    const nextButton = document.querySelector('.product-view-next-button');
    const thumbnailContainer = document.querySelector('.product-view-thumbnail-container');

    let currentIndex = 0;

    if (thumbnails.length && mainImage) {
        thumbnails.forEach((thumbnail, index) => {
            thumbnail.addEventListener('click', function() {
                mainImage.src = this.src;
            });
        });

        prevButton.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                updateCarousel();
            }
        });

        nextButton.addEventListener('click', () => {
            if (currentIndex < thumbnails.length - 3) {
                currentIndex++;
                updateCarousel();
            }
        });
    }

    function updateCarousel() {
        const offset = -currentIndex * 110;
        thumbnailContainer.style.transform = `translateX(${offset}px)`;
    }

    const wishlistButton = document.getElementById('wishlist-button');
    if (wishlistButton && !wishlistButton.dataset.eventRegistered) {
        wishlistButton.dataset.eventRegistered = "true";
        wishlistButton.addEventListener('click', function() {
            const isInWishlist = wishlistButton.classList.contains('in-wishlist');
            const url = isInWishlist ? wishlistButton.getAttribute('data-remove-url') : wishlistButton.getAttribute('data-add-url');
            const data = {
                product_id: wishlistButton.getAttribute('data-product-id'),
                category_name: wishlistButton.getAttribute('data-category-name')
            };

            console.log('Sending request to URL:', url);
            console.log('Data:', data);

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data);
                if (data.success) {
                    wishlistButton.classList.toggle('in-wishlist');
                } else {
                    console.error('Error:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    const addToCartButton = document.getElementById('add-to-cart-button');
    if (addToCartButton && !addToCartButton.dataset.eventRegistered) {
        addToCartButton.dataset.eventRegistered = "true";
        addToCartButton.addEventListener('click', function() {
            const url = addToCartButton.getAttribute('data-add-to-cart-url');
            const productId = addToCartButton.getAttribute('data-product-id');
            const categoryName = addToCartButton.getAttribute('data-category-name');
            const quantity = parseInt(document.getElementById('quantity').value);

            fetch('/get-cart-quantity/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    product_id: productId,
                    category_name: categoryName
                })
            })
            .then(response => response.json())
            .then(data => {
                const currentQuantityInCart = data.quantity_in_cart;
                const maxUnits = parseInt(document.getElementById('quantity').max);
                const newTotalQuantity = currentQuantityInCart + quantity;

                if (newTotalQuantity > maxUnits) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: `Only can add ${maxUnits - currentQuantityInCart} units. The total quantity in the cart and the quantity you want to add cannot exceed the stock.`
                    });
                } else {
                    const data = {
                        product_id: productId,
                        category_name: categoryName,
                        quantity: quantity
                    };

                    console.log('Sending request to URL:', url);
                    console.log('Data:', data);

                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Response:', data);
                        if (data.success) {
                            window.location.reload();
                        } else {
                            console.error('Error:', data.error);
                        }
                    })
                    .catch(error => console.error('Error:', error));
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }
}



















