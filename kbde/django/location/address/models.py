from django import utils
from django.db import models
from django.conf import settings
from django.contrib.gis import geos
from kbde.django import models as kbde_models
from kbde import api_client

import urllib


class GoogleGeocodeClient(api_client.Client):
    host = "https://maps.googleapis.com"
    path = "/maps/api/geocode/json?address={address}&key={api_key}"


class AbstractAddress(models.Model):
    street_1 = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)
    street_2 = models.CharField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        blank=True,
    )
    street_3 = models.CharField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        blank=True,
    )
    city = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)
    state = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)
    zip_code = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)
    zip_code_4 = models.CharField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        blank=True,
    )
    country = models.CharField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        blank=True,
    )

    street_1_slug = models.SlugField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        blank=True,
        db_index=False,
    )
    street_2_slug = models.SlugField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        blank=True,
        db_index=False,
    )
    street_3_slug = models.SlugField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        blank=True,
        db_index=False,
    )
    city_slug = models.SlugField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        blank=True,
        db_index=False,
    )
    state_slug = models.SlugField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        blank=True,
        db_index=False,
    )
    country_slug = models.SlugField(
        max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
        blank=True,
        db_index=False,
    )

    slug_field_names = [
        "street_1",
        "street_2",
        "street_3",
        "city",
        "state",
        "country",
    ]

    @classmethod
    def slug_get(cls, **kwargs):
        return cls.slug_filter(**kwargs).get()

    @classmethod
    def slug_filter(cls, **kwargs):
        slug_kwargs = {}

        for key, value in kwargs.items():

            if key not in cls.slug_field_names:
                slug_kwargs[key] = value
                continue

            slug = utils.text.slugify(value)
            slug_kwargs[f"{key}_slug"] = slug

        return cls.objects.filter(**slug_kwargs)

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

    def save(self, *args, **kwargs):
        self.set_slugs()
        return super().save(*args, **kwargs)

    def set_slugs(self):
        for field_name in self.slug_field_names:
            value = getattr(self, field_name)
            slug = utils.text.slugify(value)
            setattr(self, f"{field_name}_slug", slug)

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
