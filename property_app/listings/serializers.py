from rest_framework import serializers
from .models import Location, Property, PropertyImage

# location model serializer
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name", "slug"]

# propertyImage model serializer
class PropertyImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField() # helps to create a field in JSON that doesn't exist directly in our database model.

    class Meta:
        model = PropertyImage
        fields = ["id", "image_url", "is_primary", "alt_text"]

    def get_image_url(self, obj):
        request = self.context.get("request")

        if not obj.image:
            return None
        
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url