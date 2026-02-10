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
        request = self.context.get("request") # by accessing the request from context, serializer get's the website domain.

        if not obj.image:
            return None
        
        url = obj.image.url # get the relative path of the image.

        # combines the domain with the image path 
        return request.build_absolute_uri(url) if request else url
    
class PropertyListSerializer(serializers.ModelSerializer):
    """
    This only sends the primary_image_url with the other fields. It will help while showing a lot of properties on a single page. 
    """
    location_name = serializers.CharField(source="location.name", read_only=True)
    location_slug = serializers.CharField(source="location.slug", read_only=True)
    primary_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "external_id",
            "title",
            "address",
            "country",
            "slug",
            "location_name",
            "location_slug",
            "primary_image_url",
        ]
    
    def get_primary_image_url(self, obj):
        request = self.context.get("request")

        # searching through related images of a single property instance to find the primary image.
        primary = obj.images.filter(is_primary=True).first()
        
        if not primary or not primary.image:
            return None
        
        url = primary.image.url
        return request.build_absolute_uri(url) if request else url


class PropertyDetailSerializer(serializers.ModelSerializer):
    """
    Including all the related data for a single property detail page, using nested serializers. 
    """
    location = LocationSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True) # creates a json list of all images related to that property

    class Meta:
        model = Property
        fields = [
            "id",
            "external_id",
            "property_name",
            "title",
            "description",
            "country",
            "address",
            "location",
            "images",
            "created_at"
        ]