from django.db.models import query
from django.db.models.fields import files
from django.utils import functional
from kbde.json import encoder


class QuerySetSerializer(encoder.SerializerBase):

    def serialize(self):
        return list(self.val)


class PromiseSerializer(encoder.SerializerBase):
    
    def serialize(self):
        return self.val.__str__()


class FieldFileSerializer(encoder.SerializerBase):
    
    def serialize(self):
        if self.val:
            return self.val.url


class Encoder(encoder.Encoder):
    type_serializer_map = {
        query.QuerySet: QuerySetSerializer,
        functional.Promise: PromiseSerializer,
        files.FieldFile: FieldFileSerializer,
        **encoder.Encoder.type_serializer_map,
    }
