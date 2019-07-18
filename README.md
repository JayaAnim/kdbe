KBDE
===


# Release notes, starting at v9

- `v13`:
  - Adds OpenCV image quality analysis.
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
