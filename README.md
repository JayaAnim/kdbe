KBDE
===


# Release notes, starting at v9

- `v9`:
  - Changes API client lib
  - Changes AWS variable names in Django settings
  - Django `DEBUG` default `False`
  - Moves Django BaseView to be a mixin. Composes generic Django views from the mixin.
  - Do not do form validation in broswer. Adds Djagno setting for `HTML_VALIDATE_FORMS`, which is `False` by default
