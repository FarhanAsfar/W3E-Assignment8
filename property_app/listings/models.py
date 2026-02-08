from django.db import models
from __future__ import annotations

import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify  #slugify is used to create url-friendly slugs from strings.

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
    external_id = models.CharField(unique=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="properties")
    # 'related_name' allows to write dhaka.properties.all(), otherwise we had to write dhaka.property_set.all()

    address = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.external_id} - {self.title}"