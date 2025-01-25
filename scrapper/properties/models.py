from django.db import models


class Property(models.Model):
    # General Info
    url = models.URLField(unique=True)
    address = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_guidance = models.CharField(max_length=255, null=True, blank=True)
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    contact_info = models.TextField(null=True, blank=True)
    property_type = models.CharField(max_length=50)
    short_description = models.TextField(null=True, blank=True)

    # Additional Info
    size = models.CharField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    features = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)
    council_tax = models.CharField(null=True, max_length=255, blank=True)
    tenure = models.CharField(null=True, max_length=255, blank=True)
    parking = models.CharField(null=True, max_length=255, blank=True)
    garden = models.CharField(null=True, max_length=255, blank=True)
    accessibility = models.CharField(null=True, max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address} - £{self.price}"


class Brochures(models.Model):
    property = models.ForeignKey(Property, related_name="brochures", on_delete=models.CASCADE)
    brochure_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.brochure_url


class Image(models.Model):
    property = models.ForeignKey(Property, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField()
    floorplan = models.BooleanField(default=False)

    def __str__(self):
        return self.image_url
