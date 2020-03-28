from django.db import models
from django.contrib.gis.db import models as gis_models
from kbde.django import models as kbde_models

import urllib


class Location(models.Model):
    TYPE_COUNTRY = 1
    TYPE_STATE = 2
    TYPE_COUNTY = 3
    TYPE_MUNICIPALITY = 4
    TYPE_WARD = 5
    TYPE_VOTING_DISTRICT = 6
    TYPE_CHOICES = (
        (TYPE_COUNTRY, "Country"),
        (TYPE_STATE, "State"),
        (TYPE_COUNTY, "County"),
        (TYPE_MUNICIPALITY, "Municipality"),
        (TYPE_WARD, "Ward"),
        (TYPE_VOTING_DISTRICT, "Voting District"),
        )

    name = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)
    short_name = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, blank=True)
    code = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, blank=True)
    location_type = models.IntegerField(choices=TYPE_CHOICES)
    parents = models.ManyToManyField("Location", blank=True, related_name="children")
    external_id = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, blank=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("name", "code", "location_type")

    def get_name(self):
        return "{} {}".format(self.get_location_type_display(), self.name)

    def get_abbreviated_name(self):
        if(self.location_type <= 4): return self.name;
        return "{} - {}".format(self.parents.first().get_abbreviated_name(), self.name)

    def get_official_groups(self):
        official_groups = OfficialGroup.objects.filter(
                                                official_titles__official__address__locations=self)
        for official_group in official_groups:
            # Decorate the group with the officials that are in this location
            official_group.officials = official_group.get_officials_for_location(self)

        return official_groups

    @classmethod
    def get_all_children_from_ids(cls, location_id_list):
        locations = []
        for location_id in location_id_list:
            location = cls.objects.get(id=location_id)
            children = location.get_all_children()
            locations = locations + [location] + children
        locations = list(set(locations))
        return locations

    def get_all_parents(self, parents=[]):
        for parent in self.parents.all():
            if parent in parents:
                continue
            parents = parents + [parent]
            parents = parent.get_all_parents(parents)

        return parents

    def get_all_children(self, children=[]):
        for child in self.location_set.all():
            if child in children:
                continue
            children = children + [child]
            children = child.get_all_children(children)

        return children


class Point(models.Model):
    name = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, blank=True)
    locations = models.ManyToManyField(Location)
    point = gis_models.PointField(null=True)

    class Meta:
        unique_together = ("name", "point")


class Address(models.Model):
    locations = models.ManyToManyField(Location)
    point = models.ForeignKey(Point, on_delete=models.CASCADE, null=True, blank=True)
    street_1 = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, db_index=True)
    street_2 = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, blank=True, db_index=True)
    street_3 = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, blank=True, db_index=True)
    city = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, db_index=True)
    state = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, db_index=True)
    zip_code = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, db_index=True)
    zip_code_last_4 = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, db_index=True)
    country = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, blank=True, db_index=True)

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

    class Meta:
        unique_together = (
            "street_1",
            "street_2",
            "street_3",
            "city",
            "state",
            "zip_code",
            "country",
            )

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