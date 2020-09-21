NOT_FOUND = object()


def settings_to_template(request):
    """
    Adds from Django settings.py file
    """

    from django.conf import settings

    setting_keys = getattr(settings, "SETTINGS_TO_TEMPLATE_KEYS", [])

    settings_data = {}

    for setting_key in setting_keys:
        setting_value = getattr(settings, setting_key, NOT_FOUND) 

        if setting_value == NOT_FOUND:
            continue

        settings_data[setting_key] = setting_value

    settings_variable_name = getattr(
        settings,
        "SETTINGS_TO_TEMPLATE_VARIABLE_NAME",
        "settings",
    )

    return {
        settings_variable_name: settings_data,
    }
