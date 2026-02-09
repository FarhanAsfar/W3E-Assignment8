from __future__ import annotations
from django.db import models

import os
import uuid

from django.core.exceptions import ValidationError
from django.utils.text import slugify  #slugify is used to create url-friendly slugs from strings.

# generating dynamic file location for images for each property
def property_image_upload_path(instance: "PropertyImage", filename: str):
    """
    base folder: /properties
    {instance.property.external_id}: creates a sub-folder named after the property's id keeping all images for one property in a separate place. 
    """
    ext = os.path.splitext(filename)[1].lower()

    safe_ext = ext if ext else ".jpg" #if the file doesn't have any extension, attach .jpg

    return f"properties/{instance.property.external_id}/{uuid.uuid4().hex}{safe_ext}"

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
    
    # overriding the save() func. 
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) #turns "new york" into /new-york
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Property(models.Model):
    external_id = models.CharField(max_length=50, unique=True, editable=False)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="properties")
    # 'related_name' allows to write dhaka.properties.all(), otherwise we had to write dhaka.property_set.all()

    address = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
    
    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            
        if not self.external_id:    
            self.external_id = f"PROP-{self.pk:04d}"
            kwargs['force_insert'] = False #making sure that its updated, not inserted a new one.
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.external_id} - {self.title}"
    
    

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=property_image_upload_path)
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=150, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_primary", "created_at"]
    
    # ensuring that each property have only one primary image.
    def clean(self):
        if self.is_primary and self.property_id:
            qs = PropertyImage.objects.filter(property_id = self.property_id, is_primary = True)

            if self.pk:
                qs = qs.exclude(pk = self.pk)
            
            if qs.exists():
                raise ValidationError({"is_primary": "Only one primary image can be set per property"})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Image for {self.property.external_id} (primary={self.is_primary})"