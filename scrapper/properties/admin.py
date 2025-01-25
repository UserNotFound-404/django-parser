from django.contrib import admin

from .models import Property, Image


class PropertyAdmin(admin.ModelAdmin):
    list_display = ('address', 'price', 'property_type', 'bedrooms', 'bathrooms', 'phone_number')
    search_fields = ('address', 'property_type')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'image_url')
    search_fields = ('property__address', 'image_url')


admin.site.register(Property, PropertyAdmin)
admin.site.register(Image, ImageAdmin)
