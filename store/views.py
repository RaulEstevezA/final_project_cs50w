from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.db.models import Q, Sum, F
import json, random
from random import shuffle
from decimal import Decimal, ROUND_HALF_UP
from .product_types import PRODUCT_MODELS, CATEGORY_TO_MODEL
from .models import (Category, UserProfile, ShippingAddress, ProductImage, Wishlist, Order, OrderItem, CartItem)
from .forms import ShippingAddressForm
from django.views.decorators.csrf import csrf_exempt
import paypalrestsdk
from django.db import transaction
from django.conf import settings



# generic definitions
def get_image(product):
    images = ProductImage.objects.filter(
        content_type__pk=ContentType.objects.get_for_model(type(product)).id,
        object_id=product.id
    )
    if images.exists():
        return images.first().image.url
    return None  


def error_page(request):
    return render(request, 'store/error_page.html', {
        'error': 'No specific error provided.'
    })


def get_or_create_order(request):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(user=request.user, status='PREPARING')
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        order, created = Order.objects.get_or_create(session_key=session_key, status='PREPARING')
    return order


def get_cart_data(request):
    cart_items = get_or_create_cart(request)
    total_items = cart_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    total_price = 0.0

    for item in cart_items:
        product = item.content_object
        if product.discounted_units > 0 and item.quantity <= product.discounted_units:
            price = (product.price - (product.price * product.discount / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            price = product.price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_price += float(item.quantity) * float(price)

    return {
        'cart_items': total_items,
        'cart_total': round(total_price, 2)
    }


def merge_cart(session_key, user):
    session_cart_items = CartItem.objects.filter(session_key=session_key)
    for item in session_cart_items:
        user_cart_item, created = CartItem.objects.get_or_create(
            user=user,
            content_type=item.content_type,
            object_id=item.object_id,
            defaults={'quantity': item.quantity}
        )
        if not created:
            user_cart_item.quantity += item.quantity
            user_cart_item.save()
    session_cart_items.delete()


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user).prefetch_related('content_object')
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_items = CartItem.objects.filter(session_key=session_key).prefetch_related('content_object')
    return cart_items


@csrf_exempt
def get_cart_quantity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        category_name = data.get('category_name')

        product_model = CATEGORY_TO_MODEL.get(category_name)
        if not product_model:
            return JsonResponse({'error': 'Invalid category name'}, status=400)

        product = get_object_or_404(product_model, id=product_id)

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user,
                content_type=ContentType.objects.get_for_model(product),
                object_id=product.id
            )
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart_items = CartItem.objects.filter(
                session_key=session_key,
                content_type=ContentType.objects.get_for_model(product),
                object_id=product.id
            )

        quantity_in_cart = sum(item.quantity for item in cart_items)

        return JsonResponse({'quantity_in_cart': quantity_in_cart})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def clear_cart_buy(user):
    cart_items = CartItem.objects.filter(user=user)
    cart_items.delete()
    print("Cart cleared")
    return True


@require_POST
def clear_cart(request):
    cart_items = get_or_create_cart(request)
    cart_items.delete()
    return JsonResponse({'success': True})


def discount_stock(user):
    cart_items = CartItem.objects.filter(user=user)
    for item in cart_items:
        product = item.content_object
        if product.discounted_units > 0:
            product.discounted_units -= item.quantity
        product.stock_quantity -= item.quantity
        product.units_sold += item.quantity
        product.save()
    print("Stock discounted")


def finalize_order(user):
    discount_stock(user)
    clear_cart_buy(user)


@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        category_name = data.get('category_name')
        quantity = int(data.get('quantity', 1))

        product_model = CATEGORY_TO_MODEL.get(category_name)
        if not product_model:
            return JsonResponse({'error': 'Invalid category name'}, status=400)

        product = get_object_or_404(product_model, id=product_id)

        discounted_price = None
        max_units = product.stock_quantity
        if product.discounted_units > 0:
            discounted_price = (product.price - (product.price * product.discount / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            max_units = product.discounted_units

        if request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(product),
                object_id=product.id
            )
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart_item, created = CartItem.objects.get_or_create(
                session_key=session_key,
                content_type=ContentType.objects.get_for_model(product),
                object_id=product.id
            )

        quantity_in_cart = cart_item.quantity

        if quantity_in_cart + quantity > max_units:
            return JsonResponse({'error': f'Only can add {max_units - quantity_in_cart} units. The total quantity in the cart and the quantity you want to add cannot exceed the stock.'}, status=400)

        if created:
            cart_item.quantity = quantity
        else:
            quantity_in_cart = cart_item.quantity
            if quantity_in_cart + quantity > product.stock_quantity:
                return JsonResponse({
                    'error': f'Only can add {product.stock_quantity - quantity_in_cart} units. The total quantity in the cart and the quantity you want to add cannot exceed the stock.'
                }, status=400)
            cart_item.quantity = quantity_in_cart + quantity
        cart_item.price = discounted_price if discounted_price else product.price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        cart_item.save()

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def update_cart_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        new_quantity = int(data.get('quantity', 1))

        try:
            cart_item = CartItem.objects.get(id=item_id)
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=404)

        product = cart_item.content_object

        if new_quantity > product.stock_quantity:
            return JsonResponse({'error': f'Only {product.stock_quantity} units left in stock.'}, status=400)

        cart_item.quantity = new_quantity
        cart_item.save()

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@require_POST
def remove_cart_item(request):
    data = json.loads(request.body)
    item_id = data.get('item_id')

    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()
        return JsonResponse({'success': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item does not exist'})


@login_required
def update_account_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        phone = data.get('phone')
        confirm_password = data.get('confirm_password')

        user = request.user
        if authenticate(username=user.username, password=confirm_password):
            user.email = email
            user.profile.phone = phone
            user.save()
            user.profile.save()
            
            update_session_auth_hash(request, user)
            messages.success(request, 'Your account information has been updated.')
            return JsonResponse({'message': 'Account information updated successfully.'}, status=200)
        else:
            messages.warning(request, 'Password does not match our records.')
            return JsonResponse({'error': 'Password does not match our records.'}, status=400)
    else:
        messages.warning(request, 'Could not change Acount info, try again.')
        return JsonResponse({'error': 'Invalid request method.'}, status=405)


@login_required
def edit_shipping_address(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        profile = request.user.profile
        recipient_name = data.get('recipient_name')
        address_line1 = data.get('address')
        city = data.get('city')
        zip_code = data.get('zip_code')
        country = data.get('country')

        address, created = ShippingAddress.objects.update_or_create(
            profile=profile,
            defaults={
                'recipient_name': recipient_name,
                'full_address': address_line1,
                'city': city,
                'zip_code': zip_code,
                'country': country
            }
        )

        if created:
            messages.success(request, 'New shipping address added successfully.')
        else:
            messages.success(request, 'Shipping address updated successfully.')

        return JsonResponse({'message': 'Shipping address processed successfully.'})
    else:
        messages.error(request, 'Invalid HTTP method used.')
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


def change_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not check_password(old_password, request.user.password):
            return JsonResponse({'error': 'Old password is incorrect.'}, status=400)

        if new_password != confirm_password:
            return JsonResponse({'error': 'New passwords do not match.'}, status=400)

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user) 

        messages.success(request, 'Your password has been updated successfully.')
        return JsonResponse({'message': 'Password updated successfully.'}, status=200)

    messages.warning(request, 'Could not change password, try again.')
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@login_required
@require_POST
def remove_from_wishlist(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        category_name = data.get('category_name')
        print(f"Received remove_from_wishlist request: product_id={product_id}, category_name={category_name}")

        product_model = CATEGORY_TO_MODEL.get(category_name)
        if not product_model:
            print("Invalid category:", category_name)
            return JsonResponse({'success': False, 'error': 'Invalid category'})

        product = get_object_or_404(product_model, id=product_id)
        content_type = ContentType.objects.get_for_model(product)
        Wishlist.objects.filter(user=request.user, content_type=content_type, object_id=product.id).delete()

        return JsonResponse({'success': True})
    except Exception as e:
        print("Error in remove_from_wishlist:", e)
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def add_to_wishlist(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        category_name = data.get('category_name')
        print(f"Received add_to_wishlist request: product_id={product_id}, category_name={category_name}")

        product_model = CATEGORY_TO_MODEL.get(category_name)
        if not product_model:
            print("Invalid category:", category_name)
            return JsonResponse({'success': False, 'error': 'Invalid category'})

        product = get_object_or_404(product_model, id=product_id)
        content_type = ContentType.objects.get_for_model(product)

        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, content_type=content_type, object_id=product.id)
        if not created:
            print(f"Wishlist item already exists: {wishlist_item}")

        return JsonResponse({'success': True})
    except Exception as e:
        print("Error in add_to_wishlist:", e)
        return JsonResponse({'success': False, 'error': str(e)})
# end of generic definitions

# ------------------------------------------------------------------------------------------------------

# HOME
def home(request):
    discounted_products = []
    all_selling_products = []
    all_stock_products = []

    for model in PRODUCT_MODELS:
        products_with_discount = model.objects.filter(discounted_units__gt=0, stock_quantity__gt=0)
        
        for product in products_with_discount:
            image_url = get_image(product)
            discounted_price = product.price - (product.price * product.discount / 100)
            if image_url:
                discounted_products.append((product, image_url, discounted_price))
        
        selling_products = model.objects.filter(units_sold__gt=0, stock_quantity__gt=0)
        for product in selling_products:
            all_selling_products.append(product)

        stock_products = model.objects.filter(stock_quantity__gt=0)
        for product in stock_products:
            all_stock_products.append(product)
    
    top_sells = sorted(all_selling_products, key=lambda x: x.units_sold, reverse=True)[:3]
    top_sells_with_images = [(product, get_image(product)) for product in top_sells if get_image(product)]

    last_units = sorted(all_stock_products, key=lambda x: x.stock_quantity)[:3]
    last_units_with_images = [(product, get_image(product)) for product in last_units if get_image(product)]
    
    shuffle(discounted_products)
    discounted_products = discounted_products[:9]
    categories = Category.objects.all()
    
    cart_data = get_cart_data(request)

    return render(request, 'store/home.html', {
        'categories': categories,
        'discounted_products': discounted_products,
        'top_sells': top_sells_with_images,
        'last_units': last_units_with_images,
        'cart_items': cart_data['cart_items'],
        'cart_total': cart_data['cart_total'],
    })



# REGISTER
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmation = request.POST.get('confirmation')

        if password != confirmation:
            return render(request, 'store/register.html', {'message': 'Passwords must match.'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'store/register.html', {'message': 'Username already exists.'})

        session_key = request.session.session_key 

        user = User.objects.create(username=username, email=email, password=make_password(password))
        UserProfile.objects.create(user=user)
        auth_login(request, user)
        
        if session_key:
            merge_cart(session_key, user)
        
        return redirect('store:home')
    else:
        cart_data = get_cart_data(request)

        return render(request, 'store/register.html', {
            'cart_items': cart_data['cart_items'],
            'cart_total': cart_data['cart_total'],
        })


# LOGIN
def login(request):
    message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            session_key = request.session.session_key
            auth_login(request, user)
            if session_key:
                merge_cart(session_key, user)
            return redirect('store:home')
        else:
            message = "Invalid username or password."
    
    cart_data = get_cart_data(request)

    return render(request, 'store/login.html', {
        'message': message,
        'cart_items': cart_data['cart_items'],
        'cart_total': cart_data['cart_total'],
    })


#LOGOUT
@login_required
def logout_view(request):
    if request.user.is_authenticated:
        clear_cart_buy(request.user)
    logout(request)
    return HttpResponseRedirect(reverse("store:home"))


# PROFILE
@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()

        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)
        profile.city = request.POST.get('city', profile.city)
        profile.zip_code = request.POST.get('zip_code', profile.zip_code)
        profile.country = request.POST.get('country', profile.country)
        profile.save()

        messages.success(request, 'Your profile was successfully updated!')
        return redirect('store:profile') 

    cart_data = get_cart_data(request)

    return render(request, 'store/profile.html', {
        'user': request.user,
        'profile': profile,
        'cart_items': cart_data['cart_items'],
        'cart_total': cart_data['cart_total'],     
    })
        

# CATEGORIES
def category(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    category_products = {}

    for model in PRODUCT_MODELS:
        products = model.objects.filter(category=category)
        if products.exists():
            product_list = []
            for product in products:
                content_type = ContentType.objects.get_for_model(model)
                image = ProductImage.objects.filter(content_type=content_type, object_id=product.id).first()
                image_url = image.image.url if image else None
                discounted_price = None
                discount_percentage = 0
                if product.discounted_units > 0:
                    discounted_price = product.price - (product.price * product.discount / 100)
                    discount_percentage = product.discount
                product_list.append((product, image_url, discounted_price, discount_percentage))
            category_products[model.__name__] = product_list

    categories = Category.objects.all()
    cart_data = get_cart_data(request)

    return render(request, 'store/category.html', {
        'categories': categories,
        'category': category,
        'category_products': category_products,
        'cart_items': cart_data['cart_items'],
        'cart_total': cart_data['cart_total'],
    })


# PRODUCT VIEW
def product_view(request, category_name, product_id):
    product_model = CATEGORY_TO_MODEL.get(category_name)
    if not product_model:
        return render(request, 'store/error_page.html', {
            'error': f'No product model found for category: {category_name}'
        })

    product = get_object_or_404(product_model, id=product_id)
    images = ProductImage.objects.filter(
        content_type__pk=ContentType.objects.get_for_model(product_model).id,
        object_id=product.id
    )

    # filter out unwanted fields
    unwanted_fields = ["id", "stock_quantity", "units_sold", "category", "price", "discount", "discounted_units"]

    # filter fields
    product_dict = model_to_dict(product, fields=[field.name for field in product._meta.fields if field.name not in unwanted_fields])

    main_image = images[0].image.url if images else None

    discounted_price = None
    max_units = product.stock_quantity
    if product.discounted_units > 0:
        discounted_price = product.price - (product.price * product.discount / 100)
        max_units = product.discounted_units

    # verify wishlist
    is_in_wishlist = False
    if request.user.is_authenticated:
        content_type = ContentType.objects.get_for_model(product)
        is_in_wishlist = Wishlist.objects.filter(user=request.user, content_type=content_type, object_id=product.id).exists()

    categories = Category.objects.all()
    cart_data = get_cart_data(request)

    return render(request, 'store/product_view.html', {
        'categories': categories,
        'product': product,
        'product_details': product_dict,
        'main_image': main_image,
        'images': images,
        'discounted_price': discounted_price,
        'max_units': max_units,
        'is_in_wishlist': is_in_wishlist,
        'cart_items': cart_data['cart_items'],
        'cart_total': cart_data['cart_total'],
    })


# ORDERS
@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    cart_data = get_cart_data(request)

    return render(request, 'store/orders.html', {
        'orders': user_orders, 
        'cart_items': cart_data['cart_items'],
        'cart_total': cart_data['cart_total'],
        })


# CART
def cart(request):
    categories = Category.objects.all()
    cart_data = get_cart_data(request)
    cart_items = get_or_create_cart(request) 

    for item in cart_items:
        product = item.content_object
        item.max_units = product.stock_quantity
        if product.discounted_units > 0:
            item.max_units = product.discounted_units

    for item in cart_items:
        product = item.content_object
        if product.discounted_units > 0 and product.discounted_units >= item.quantity:
            item.price = (product.price - (product.price * product.discount / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            item.price = product.price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    cart_total = sum((item.quantity * item.price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) for item in cart_items)

    return render(request, 'store/cart.html', {
        'cart_items': cart_data['cart_items'],
        'categories': categories,
        'cart_total': cart_total,
        'order_items': cart_items, 
    })


# SEARCH
def search(request):
    query = request.GET.get('query', '')
    all_results = []

    if query:
        for model in PRODUCT_MODELS:
            # search in title
            model_results = model.objects.filter(
                Q(title__icontains=query)
            )
            all_results.extend(model_results)
    
    # take the image
    products_with_images = []
    for product in all_results:
        image_url = get_image(product)
        discounted_price = None
        if product.discounted_units > 0:
            discounted_price = product.price - (product.price * product.discount / 100)
        products_with_images.append((product, image_url, discounted_price))
    
    categories = Category.objects.all()
    cart_data = get_cart_data(request)

    return render(request, 'store/search.html', {
        'categories': categories,
        'query': query,
        'products_with_images': products_with_images,
        'cart_items': cart_data['cart_items'],
        'cart_total': cart_data['cart_total'],
    })


# WISHLIST
@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    products = []
    for item in wishlist_items:
        product = item.product
        image_url = get_image(product)
        discounted_price = None
        if product.discounted_units > 0:
            discounted_price = product.price - (product.price * product.discount / 100)
        products.append((product, image_url, discounted_price))

    categories = Category.objects.all()
    cart_data = get_cart_data(request)

    return render(request, 'store/wishlist.html', {
        'products': products,
        'categories': categories,
        'cart_items': cart_data['cart_items'],
        'cart_total': cart_data['cart_total'],
    })



# CHECKOUT
def checkout(request):
    categories = Category.objects.all()
    cart_data = get_cart_data(request)
    cart_items = get_or_create_cart(request)

    for item in cart_items:
        product = item.content_object
        max_units = product.stock_quantity
        if product.discounted_units > 0 and product.discounted_units >= item.quantity:
            item.price = (product.price - (product.price * product.discount / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            max_units = product.discounted_units
        else:
            item.price = product.price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        item.max_units = max_units

    cart_total = sum((item.quantity * item.price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) for item in cart_items)

    shipping_address = None

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            shipping_address = profile.shipping_addresses.first()
        except UserProfile.DoesNotExist:
            pass

    return render(request, 'store/checkout.html', {
        'cart_items': cart_data['cart_items'],
        'categories': categories,
        'cart_total': cart_total,
        'order_items': cart_items,
        'shipping_address': shipping_address,
    })


# ORDER DETAIL
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    cart_data = get_cart_data(request)
    return render(request, 'store/order_detail.html', {
        'order': order, 
        'order_items': order_items,
        'cart_items': cart_data['cart_items'],
        'cart_total': cart_data['cart_total'],
        })


# TYPES PAYMENT
def process_payment(request):
    payment_method = request.POST.get('payment_method')
    if payment_method == 'paypal':
        return redirect('store:paypal_payment')
    elif payment_method == 'credit_card':
        return redirect('store:credit_card_payment')
    elif payment_method == 'transfer':
        return redirect('store:transfer_payment')
    else:
        return JsonResponse({'error': 'Invalid payment method selected.'}, status=400)
    

# PAYPAL PAYMENT
paypalrestsdk.configure({
  "mode": settings.PAYPAL_MODE,  # sandbox or live
  "client_id": settings.PAYPAL_CLIENT_ID,
  "client_secret": settings.PAYPAL_CLIENT_SECRET})


def paypal_payment(request):
    if request.method == 'POST':
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": "http://localhost:8000/payment/execute/",
                "cancel_url": "http://localhost:8000/"},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Your Purchase",
                        "sku": "001",
                        "price": "10.00",
                        "currency": "USD",
                        "quantity": 1}]},
                "amount": {
                    "total": "10.00",
                    "currency": "USD"},
                "description": "This is the payment transaction description."}]})

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)
                    return redirect(approval_url)
        else:
            return render(request, 'store/payment_error.html', {'error': payment.error})
    return render(request, 'store/payment.html')


@login_required
@csrf_exempt
def payment_execute(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        user = request.user

        # Reautenticar al usuario si es necesario
        if not user.is_authenticated:
            user = authenticate(username=user.username)
            if user is not None:
                auth_login(request, user)

        try:
            shipping_address = user.profile.shipping_addresses.first()
            if not shipping_address:
                return render(request, 'store/payment_error.html', {'error': 'Shipping address is missing.'})

            order = Order.objects.create(
                user=user,
                shipping_address=shipping_address.full_address,
                shipping_city=shipping_address.city,
                status='CONFIRMING_PAYMENT',
                payment_method='PAYPAL'
            )

            cart_items = CartItem.objects.filter(user=user)
            for cart_item in cart_items:
                product = cart_item.content_object
                if product.discounted_units > 0 and cart_item.quantity <= product.discounted_units:
                    price_at_purchase = (product.price - (product.price * product.discount / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                else:
                    price_at_purchase = product.price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                OrderItem.objects.create(
                    order=order,
                    content_type=cart_item.content_type,
                    object_id=cart_item.object_id,
                    quantity=cart_item.quantity,
                    price_at_purchase=price_at_purchase
                )

            finalize_order(user)

            cart_data = get_cart_data(request)

            return render(request, 'store/payment_success.html', {
                'cart_items': cart_data['cart_items'],
                'cart_total': cart_data['cart_total'],
            })
        except UserProfile.DoesNotExist:
            return render(request, 'store/payment_error.html', {'error': 'User profile not found.'})
    else:
        cart_data = get_cart_data(request)
        return render(request, 'store/payment_error.html', {
            'error': payment.error,
            'cart_items': cart_data['cart_items'],
            'cart_total': cart_data['cart_total'],
        })
# END PAYPAL PAYMENT


# CREDIT CARD PAYMENT
def credit_card_payment(request):
    cart_data = get_cart_data(request)

    return render(request, 'store/credit_card.html', {
        'cart_items': cart_data['cart_items'],
        'cart_total': cart_data['cart_total'],
    })


def credit_card_execute(request):
    if request.method == 'POST':
        if 'confirm_payment' in request.POST:
            user = request.user

            try:
                shipping_address = user.profile.shipping_addresses.first()
                if not shipping_address:
                    return render(request, 'store/payment_error.html', {'error': 'Shipping address is missing.'})

                order = Order.objects.create(
                    user=user,
                    shipping_address=shipping_address.full_address,
                    shipping_city=shipping_address.city,
                    status='CONFIRMING_PAYMENT',
                    payment_method='CREDIT_CARD'
                )

                cart_items = CartItem.objects.filter(user=user)
                for cart_item in cart_items:
                    product = cart_item.content_object
                    if product.discounted_units > 0 and cart_item.quantity <= product.discounted_units:
                        price_at_purchase = product.price - (product.price * product.discount / 100)
                    else:
                        price_at_purchase = product.price

                    OrderItem.objects.create(
                        order=order,
                        content_type=cart_item.content_type,
                        object_id=cart_item.object_id,
                        quantity=cart_item.quantity,
                        price_at_purchase=price_at_purchase
                    )

                finalize_order(user)
                
                cart_data = get_cart_data(request)

                return render(request, 'store/payment_success.html', {
                    'cart_items': cart_data['cart_items'],
                    'cart_total': cart_data['cart_total'],
                })
            except UserProfile.DoesNotExist:
                return render(request, 'store/payment_error.html', {'error': 'User profile not found.'})
        else:
            cart_data = get_cart_data(request)
            return render(request, 'store/payment_error.html', {
                'error': 'Payment was cancelled or failed.',
                'cart_items': cart_data['cart_items'],
                'cart_total': cart_data['cart_total'],
                })
    return redirect('store:checkout')
# END CREDIT CARD PAYMENT


# TRANSFER PAYMENT
@login_required
@csrf_exempt
def transfer_payment(request):
    if request.method == 'POST':
        user = request.user

        try:
            shipping_address = user.profile.shipping_addresses.first()
            if not shipping_address:
                return render(request, 'store/payment_error.html', {'error': 'Shipping address is missing.'})

            order = Order.objects.create(
                user=user,
                shipping_address=shipping_address.full_address,
                shipping_city=shipping_address.city,
                status='CONFIRMING_PAYMENT',
                payment_method='TRANSFER'
            )

            cart_items = CartItem.objects.filter(user=user)
            for cart_item in cart_items:
                product = cart_item.content_object
                if product.discounted_units > 0 and cart_item.quantity <= product.discounted_units:
                    price_at_purchase = product.price - (product.price * product.discount / 100)
                else:
                    price_at_purchase = product.price

                OrderItem.objects.create(
                    order=order,
                    content_type=cart_item.content_type,
                    object_id=cart_item.object_id,
                    quantity=cart_item.quantity,
                    price_at_purchase=price_at_purchase
                )

            finalize_order(user)

            cart_data = get_cart_data(request)

            return render(request, 'store/transfer.html', {
                'order': order,
                'cart_items': cart_data['cart_items'],
                'cart_total': cart_data['cart_total'],
            })
        except UserProfile.DoesNotExist:
            return render(request, 'store/payment_error.html', {'error': 'User profile not found.'})
    return redirect('store:checkout')
# END TRANFER PAYMENT


