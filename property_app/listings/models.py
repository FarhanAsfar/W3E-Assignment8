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