from django.db.models import query
from django.utils import functional
from kbde.json import encoder


class QuerySetSerializer(encoder.SerializerBase):

    def serialize(self):
        return list(self.val)


class Encoder(encoder.Encoder):
    type_serializer_map = {
        query.QuerySet: QuerySetSerializer,
        functional.Promise: encoder.ToStringSerializer,
        **encoder.Encoder.type_serializer_map,
    }
