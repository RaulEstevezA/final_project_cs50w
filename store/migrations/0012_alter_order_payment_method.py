# Generated by Django 5.0.1 on 2024-07-01 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_order_bank_account_number_order_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('PAYPAL', 'PayPal'), ('CREDIT_CARD', 'Credit Card'), ('TRANSFER', 'Transfer')], default='PAYPAL', max_length=20, verbose_name='Payment Method'),
        ),
    ]
