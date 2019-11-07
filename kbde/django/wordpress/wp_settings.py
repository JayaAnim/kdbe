from django.conf import settings


WORDPRESS_TABLE_PREFIX = getattr(settings, 'WORDPRESS_TABLE_PREFIX', 'wp_')
WORDPRESS_LOGGED_IN_KEY = getattr(settings, 'WORDPRESS_LOGGED_IN_KEY')
WORDPRESS_LOGGED_IN_SALT = getattr(settings, 'WORDPRESS_LOGGED_IN_SALT')
WORDPRESS_COOKIEHASH = getattr(settings, 'WORDPRESS_COOKIEHASH', None)
WORDPRESS_LOGIN_URL = getattr(settings, "WORDPRESS_LOGIN_URL", "wp-login.php")
WORDPRESS_DEV_USER_ID = getattr(settings, "WORDPRESS_DEV_USER_ID", None)
