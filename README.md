KBDE
===


# Release notes, starting at v9

- `v22`:
  - Fixes some issues with the defualt auth settings. Adds a mechanism for WP debug users so that all developers don't need to authenticate through WP.
- `v21`:
  - Fixes a bug with user models being defined in django.settings.
- `v20`:
  - Early-stage forms module. Auth settings. Wordpress support.
- `v19`:
  - Adds a `self.get_success_message()` function to Edit mixin.
- `v18`:
  - Changes the method for facial detection in the `cv.image` module. Involves some non-backwards-compatible changes to the interface of that module.
  - Fixes a timezone setting bug in `django.mixins`.
  - Fixes face classifier issue.
- `v17`:
  - Adds a check to `data.serialize.Serializable` to ensure that it is being used properly.
  - Moves image functionality into `cv.image`.
- `v16`:
  - Removes requirement that `DEBUG` needs to be an int. `DEBUG` can now be any value, and `bool()` evaluation will determine the `DEBUG` setting.
  - Changes JSON response in `api_client` to not decode an empty response payload.
- `v15`:
  - Adds mixins for Soft Delete and for org-limited models.
  - Adds logging to `stdout` based on the `APP_LOG_LEVEL` env var to Django settings.
- `v14`:
  - Adds email and Trello `send_to_` functions, with form and view mixins.
- `v13`:
  - Adds OpenCV image quality analysis.
  - Changes the interface for the `django.utils.send_email()`.
  - Adds `django.utils.send_to_trello()`, which creates a new trello card via email.
  - Adds `DEBUG_EMAIL` to `django.settings`.
  - Adds `EMAIL_SUBJECT_PREFIX` to `django.settings`.
  - Removes `SERVER_EMAIL` from `django.settings`. This will need to be set manually in `settings.py`
  - Removes any `install_requires` from this package. Users will need to install dependent packages manually.
- `v12`:
  - Adds multipart/form-data as a content type in the API client.
- `v11`:
  - Adds a Django model for users which are identified via email address, instead of a username.
- `v10`:
  - Adds a Django model for scheduling.
- `v9`:
  - Changes API client lib.
  - Changes AWS variable names in Django settings.
  - Django `DEBUG` default `False`.
  - Moves Django BaseView to be a mixin. Composes generic Django views from the mixin.
  - Do not do form validation in broswer. Adds Django setting for `HTML_VALIDATE_FORMS`, which is `False` by default.
