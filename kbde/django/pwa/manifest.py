from django.conf import settings
from django.templatetags import static

import copy


class Manifest:
    fields = [
        "icons",
        "name",
        "background_color",
        "categories",
        "description",
        "dir_",
        "display",
        "iarc_rating_id",
        "lang",
        "orientation",
        "prefer_related_applications",
        "related_applications",
        "scope",
        "screenshots",
        "short_name",
        "shortcuts",
        "start_url",
        "theme_color",
    ]
    required_fields = [
        "icons",
        "name",
    ]
    field_defaults = {
        "display": "standalone",
        "prefer_related_applications": False,
        "start_url": "/",
    }

    def __init__(self, **kwargs):
        # Verify requred args
        for field in self.required_fields:
            value = kwargs.get(field)
            assert value, (
                f"Manifest requires {field}, but no value was given"
            )

        # Add defaults for args which are not passed
        data = copy.deepcopy(self.field_defaults)
        copied_kwargs = copy.deepcopy(kwargs)
        data.update(copied_kwargs)

        self.data = data
        
    @classmethod
    def from_settings(cls, settings_prefix="PWA_"):
        data = {}

        for field in cls.fields:
            setting_name = f"{settings_prefix}{field.upper().rstrip('_')}"

            value = getattr(settings, setting_name, None)

            if field in cls.required_fields:
                assert value is not None, (
                    f"Must set {setting_name} setting"
                )

            if value is None:
                continue

            data[field] = value

        return cls(**data)

    def to_dict(self):
        data = {}

        for field in self.fields:
            value = self.data.get(field)
            if value is None:
                continue

            if field == "icons":
                value = value.copy()
                for icon in value:
                    icon["src"] = static.static(icon["src"])

            data[field.rstrip("_")] = value

        return data
