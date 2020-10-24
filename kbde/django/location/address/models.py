from django.db import models
from kbde.django import models as kbde_models


class AbstractAddress(models.Model):
    street_1 = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)
    street_2 = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, blank=True)
    street_3 = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, blank=True)
    city = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)
    state = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)
    zip_code = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)
    zip_code_4 = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, blank=True)
    country = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, blank=True)

    class Meta:
        abstract = True
        unique_together = (
            "street_1",
            "street_2",
            "street_3",
            "city",
            "state",
            "zip_code",
            "country",
            )

    def __str__(self):
        fields = [
            self.street_1,
            self.street_2,
            self.street_3,
            self.city,
            self.state,
            self.zip_code,
            self.country,
            ]
        fields = [f for f in fields if f]
        return ", ".join(fields)

    def get_location_with_type(self, type):
        locations = self.locations.all()
        for location in locations:
            if location.location_type == type:
                return location
            parents = location.get_all_parents()
            for parent_location in parents:
                if parent_location.location_type == type:
                    return parent_location

    def get_url_safe(self):
        address_str = self.__str__()
        return urllib.parse.quote(address_str)

    def get_within_state(self):
        fields = [
            self.street_1,
            self.street_2,
            self.street_3,
            self.city,
            self.zip_code,
            ]
        fields = [f for f in fields if f]
        return " ".join(fields)

    # Geocoding

    def geocode(self):
        self.point = self.create_geocode_point()
        self.save()

    def create_geocode_point(self):
        coords = self.get_coords()

        if coords is None:
            return None
        
        geos_point = geos.Point(*coords)

        point = Point(point=geos_point)
        point.save()

        return point

    def get_coords(self):
        """
        Returns the coordinates for this address
        """
        result = GoogleGeocodeClient().get(
            address=self.get_url_safe(),
            api_key=settings.GEOCODE_API_KEY,
        )

        results = result["results"]

        if not results:
            return None

        result = results[0]
        geometry = result["geometry"]
        location = geometry["location"]

        return location["lng"], location["lat"]
