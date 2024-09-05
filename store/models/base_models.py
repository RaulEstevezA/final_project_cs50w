from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username


class ShippingAddress(models.Model):
    profile = models.ForeignKey(UserProfile, related_name="shipping_addresses", on_delete=models.CASCADE)
    recipient_name = models.CharField(max_length=100, verbose_name="Recipient Name", default="Unknown Recipient")
    full_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.recipient_name} - {self.full_address}, {self.city}, {self.zip_code}, {self.country}"

    class Meta:
        unique_together = ('profile', 'city', 'zip_code', 'country', 'recipient_name')


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        unique_together = ('name', 'parent',)
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock_quantity = models.PositiveIntegerField(default=0)
    discounted_units = models.IntegerField(default=0)
    units_sold = models.PositiveIntegerField(default=0)

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count()
        else:
            return 0

    class Meta:
        abstract = True 

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.content_object} x{self.quantity}'


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('CONFIRMING_PAYMENT', 'Confirming Payment'),
        ('PREPARING', 'Preparing'),
        ('AWAITING_PICKUP', 'Awaiting Pickup'),
        ('EN_ROUTE', 'En Route'),
        ('DELIVERED', 'Delivered'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('PAYPAL', 'PayPal'),
        ('CREDIT_CARD', 'Credit Card'),
        ('TRANSFER', 'Transfer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_address = models.TextField(verbose_name="Shipping Address")
    shipping_city = models.CharField(max_length=100, verbose_name="Shipping City")
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='CONFIRMING_PAYMENT', verbose_name="Order Status")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='PAYPAL',verbose_name="Payment Method")
    bank_account_number = models.CharField(max_length=30, blank=True, null=True, verbose_name="Bank Account Number")

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'
    
    def save(self, *args, **kwargs):
        if self.payment_method == 'TRANSFER':
            self.bank_account_number = '1234567890'  # Example bank account number
        else:
            self.bank_account_number = None
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(default=1)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.content_object} x{self.quantity} in order {self.order.id}'


class ProductImage(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product}"


class Review(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.product}"

