from django.contrib import admin
from store.models import Category, UserProfile, Order, OrderItem, Review, ProductImage, Motherboard, CPU, GraphicsCard, RAM, ComputerCase, PowerSupply, CPUAirCooler, CPULiquidCooler, CaseFan, SoundCard, HardDrive, SSD, Monitor, Keyboard, Headset, Mouse, WebCam
from django.contrib.contenttypes.admin import GenericTabularInline


class ProductImageInline(GenericTabularInline):
    model = ProductImage
    extra = 1


# Base Product Admin
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('title', 'price', 'stock_quantity', 'discount', 'discounted_units', 'category')


# Function to register product models
def register_product_model(model):
    admin.site.register(model, ProductAdmin)


# Register Product models with ProductAdmin
product_models = [Motherboard, CPU, GraphicsCard, RAM, ComputerCase, PowerSupply,
                  CPUAirCooler, CPULiquidCooler, CaseFan, SoundCard, HardDrive, 
                  SSD, Monitor, Keyboard, Headset, Mouse, WebCam]


for model in product_models:
    register_product_model(model)


# Register other models normally
admin.site.register(Category)
admin.site.register(UserProfile)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)


