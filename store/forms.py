# store/forms.py

from django import forms
from .models import ShippingAddress

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['recipient_name', 'full_address', 'city', 'zip_code', 'country']
