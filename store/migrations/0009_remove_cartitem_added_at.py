# Generated by Django 5.0.1 on 2024-06-17 23:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_cartitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='added_at',
        ),
    ]
