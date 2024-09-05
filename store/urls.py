from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('cart/', views.cart, name='cart'),
    path('search/', views.search, name='search'),
    path("logout", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("orders/", views.orders, name="orders"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path('update_account_info/', views.update_account_info, name='update_account_info'),
    path('edit-shipping-address/', views.edit_shipping_address, name='edit_shipping_address'),
    path('change_password/', views.change_password, name='change_password'),
    path('category/<str:category_name>/', views.category, name='category'),
    path('error/', views.error_page, name='error_page'),
    path('category/<str:category_name>/product/<int:product_id>/', views.product_view, name='product_view'),
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('get-cart-quantity/', views.get_cart_quantity, name='get_cart_quantity'),
    path('cart/', views.cart, name='cart'),
    path('update_cart_item/', views.update_cart_item, name='update_cart_item'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('remove_cart_item/', views.remove_cart_item, name='remove_cart_item'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment/execute/', views.payment_execute, name='payment_execute'),
    path("payment/", views.paypal_payment, name="paypal_payment"),
    path("credit_card/", views.credit_card_payment, name="credit_card_payment"),
    path("transfer/", views.transfer_payment, name="transfer_payment"),
    path('credit-card/execute/', views.credit_card_execute, name='credit_card_execute'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]