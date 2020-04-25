import json
import decimal
import datetime

try:
    import django
except ImportError:
    django = None


class Encoder(json.JSONEncoder):
    serialize_method_name = "serialize"
    decimal_types = (
        decimal.Decimal,
        )
    datetime_types = (
        datetime.datetime,
        datetime.date,
        datetime.time,
        )

    def default(self, obj):
        serialize = getattr(obj, self.serialize_method_name, None)

        if callable(serialize):
            return serialize()

        if isinstance(obj, self.decimal_types):
            return self.handle_decimal(obj)

        if isinstance(obj, self.datetime_types):
            return self.handle_datetime(obj)

        if django and isinstance(obj, django.db.models.query.QuerySet):
            return self.handle_django_queryset(obj)
        
        return super().default(obj)

    def handle_decimal(self, obj):
        return str(obj)

    def handle_datetime(self, obj):
        return obj.isoformat()

    def handle_django_queryset(self, obj):
        return list(obj)
