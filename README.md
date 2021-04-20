KBDE
===

kBuilds Basic Development Environment. A foundational library for Python and Django.


# Installing

KBDE can be installed to a specific project, as with any Python dependency. It can also be installed system-wide to take advantage of commandline tools.


## In a Python project

The following line can be added to your `requirements.txt` file:

```
git+https://gitlab.com/kb_git/kbde@v1
```

>Be sure to replace `v1` with the correct version.


## System-wide

To take advantage of some useful commandline tools, you can install KBDE system-wide.

```
sudo python3 -m pip install git+https://gitlab.com/kb_git/kbde
```

See [KBDE CLI](kbde/kbde_cli/README.md) for more information.


# Release notes, starting at v9

- `v65`:
  - Removes `django.mixins.EmailForm`.
  - Moves `django.mixins` and `django.views` into a single `django.views` module.
  - Adds basic JSON views module to `django`.
  - Adds Table, Delete, and Form views.
- `v64`:
  - Adds ETL library.
- `v63`:
  - Moves `coreui.scss` to `coreui.sass` in `django.coreui`.
  - Adds view partials for `django` and `django.coreui`.
  - License update.
  - Adds view unique identifiers for each instance, `view.id`.
  - Adds reusable `django.views.LoginView` class, and `django.urls.auth` module.
- `v62`:
  - Renames the template block `page_css` to `page_styles` in `django/templates/kbde/page.html`.
  - Changes the main css file names from `base` to `page` when using `django-pipeline`.
- `v61`:
  - Adds a flag to the `django.mixins.Permissions` class to inform permission classes of whether or not a view is dispatching.
- `v60`:
  - Improves `django.mixins.SuccessUrlNext`.
- `v59`:
  - Memquery module updates.
  - Removes `django.mixins.RelatedObjectEdit` and moves that functionality into `django.mixins.RelatedObject`.
  - Adds `related_object` to `context_data` in `django.mixins.RelatedObject`.
- `v58`:
  - Fixes `django.mixins.PostToGet`.
- `v57`:
  - Adds support for a `base.sass` file, instead of just `base.scss`, in Django Pipeline.
- `v56`:
  - Adds KBDE Django views.
  - Adds user-allowed model classmethods to limit what individual users are allowed to see.
  - Adds permissioning classes for Django.
  - Adds template filter to check permissions on another view.
- `v55`:
  - Improvements to `django.utils`.
  - Django base mixin.
- `v54`:
  - Removes support for several unused packages.
  - Updates to CLI.
  - Reorganizes some packages.
- `v53`:
  - Adds new Django mixins for redirecting based on the `next` GET parameter. Updates form partial to match.
  - Adds `django_rq` to Django settings automatically.
- `v52`:
  - Separates the Django BgProcess model into abstract and concrete classes.
  - Creates a new Django reporting model to inherit from the BgProcess abstract class. Old versions of the Report class are now deprecated.
- `v51`:
  - Adds user email verification model for Django.
- `v50`:
  - Removes CoreUI partials lib.
  - Adds Django form partial.
- `v49`:
  - Adds `DEBUG_PHONE_NUMBER` to Django settings.
  - Adds CoreUI Django app.
  - Adds Django Pipeline Sass config to Django settings.
- `v48`:
  - Adds slug fields for Django Address class.
  - Adds Django mixin for search.
- `v47`:
  - Adds a scraper Python library.
  - Changes `django.location.models.Address` fields.
  - Abstracts `django.location.models.Address` into another class.
- `v46`:
  - Moves `apt` module into the `install` module. Adds several install scripts.
  - Adds SMS validation with Twilio.
- `v45`:
  - Changes Django `RelatedObject` mixin. Removes deprecated relational mixins.
- `v44`:
  - Adds new cli script and command framework.
  - Adds `apt` module to pre-configure environments.
  - Adds shell mixins for running commands against the host OS.
- `v43`:
  - Adds a Django database import tool.
- `v42`:
  - Adds leader identification for GCP.
  - Adds geocoding to Django location module for addresses.
  - Moves Django report to Bg Process model.
- `v41`:
  - Changes Django `location` models to use explicit id fields for pk. This will break models which rely on this app.
  - Changes Django `bg_process` models to use explicit id fields for pk. This will break models which rely on this app.
  - Adds a template context processor which allows settings.py variables to be selectively exposed to all templates.
  - Removes the nullable option for `django.location.models.Point`.
- `v40`:
  - Adds a model-based Background Processing module for Django, based on `django-rq`.
- `v39`:
  - Better API exception handling for errors with response data.
- `v38`:
  - Overhauls Django RelatedObject mixin.
  - Adds `LOGIN_URL` to the Django settings. Defaults to the Django default url name.
- `v37`:
  - Adds `fill_form` method to PDFtk.
  - Fixes issue with `RelatedObject` mixin in Django.
  - Uses `dj-redis-url` for configuring RQ.
  - Adds `RelatedObjectForm` mixin to Django.
- `v36`:
  - Allows printing of rendered PDFs with passwords on them.
- `v35`:
  - Adds GCP bindings for the `gcloud` command.
  - Adds RQ config and utils.
  - Refines related object mixin.
- `v34`:
  - Adds a management command for creating and maintaining Django superusers via the ADMINS setting.
  - Adds Django utils function for getting the hostname from a request.
- `v33`:
  - Adds basic charting lib.
- `v32`:
  - Updates Bootstrap and Popper.js dependencies.
- `v31`:
  - Adds reporting Django app.
- `v30`:
  - Adds geo point to the Point model from django.location.
- `v29`:
  - Makes email login case insensitive.
  - Removes the KBDE Django Base Mixin. All functionality ported to templates, template context processors, and middleware.
- `v28`:
  - Adds Python bindings for PDFTK.
- `v27`:
  - Adds location models for Addresses, Areas, and Points.
  - Removes the Django Edit mixin in favor of Django's `SuccessMessageMixin`.
- `v26`:
  - Adds related-object-limiting and delete-view mixins for Django.
- `v25`:
  - Makes the WordPress authentication system compaitble with Django's. No need for a second set of access mixins.
- `v24`:
  - Adds SSL redirect variable for Django.
- `v23`:
  - Removes `LOGIN_URL` setting.
  - Converts WP models to use a model manager instead of a mixin.
- `v22`:
  - Fixes some issues with the defualt auth settings.
  - Adds a mechanism for WP debug users so that all developers don't need to authenticate through WP.
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
