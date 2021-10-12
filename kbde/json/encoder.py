import json, decimal, datetime, uuid


class SerializerBase:
    
    def __init__(self, val):
        self.val = val


class ToStringSerializer(SerializerBase):

    def serialize(self):
        return str(self.val)


class DateTimeSerializer(SerializerBase):

    def serialize(self):
        return self.val.isoformat()


class Encoder(json.JSONEncoder):
    type_serializer_map = {
        decimal.Decimal: ToStringSerializer,
        datetime.datetime: DateTimeSerializer,
        datetime.date: DateTimeSerializer,
        datetime.time: DateTimeSerializer,
        uuid.UUID: ToStringSerializer,
    }

    def default(self, obj):
        for t, serializer_class in self.type_serializer_map.items():
            if isinstance(obj, t):
                obj = serializer_class(obj)
                break

        serialize = self.get_serializer_method(obj)

        if callable(serialize):
            return serialize()

        return super().default(obj)

    def get_serializer_method(self, obj):
        return getattr(obj, "serialize", None)
