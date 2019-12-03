from django.db import models
from django import utils
from django.utils.six.moves import urllib
from django.conf import settings
from django.contrib.auth import models as auth_models

from . import wp_settings, cookie as wp_cookie

import phpserialize


class WordpressManager(models.Manager):
    
    def get_queryset(self):
        return super().get_queryset().using("wordpress")


class WpOptions(models.Model):
    option_id = models.BigAutoField(primary_key=True)
    option_name = models.CharField(unique=True, max_length=191)
    option_value = models.TextField()
    autoload = models.CharField(max_length=20)

    objects = WordpressManager()

    class Meta:
        managed = False
        db_table = 'wp_options'

    @classmethod
    def get_site_url(cls):
        url = cls.objects.get(option_name="siteurl").option_value
        return url.rstrip('/\\')

    @classmethod
    def get_login_url(cls):
        return urllib.parse.urljoin(cls.get_site_url(), wp_settings.WORDPRESS_LOGIN_URL)


class WpUsermeta(models.Model):
    umeta_id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    meta_key = models.CharField(max_length=255, blank=True, null=True)
    meta_value = models.TextField(blank=True, null=True)

    objects = WordpressManager()

    class Meta:
        managed = False
        db_table = 'wp_usermeta'


class WpUsers(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    user_login = models.CharField(max_length=60)
    user_pass = models.CharField(max_length=255)
    user_nicename = models.CharField(max_length=50)
    user_email = models.CharField(max_length=100)
    user_url = models.CharField(max_length=100)
    user_registered = models.DateTimeField()
    user_activation_key = models.CharField(max_length=255)
    user_status = models.IntegerField()
    display_name = models.CharField(max_length=250)

    objects = WordpressManager()

    is_anonymous = False
    is_authenticated = True

    class Meta:
        managed = False
        db_table = 'wp_users'

    @classmethod
    def get_from_request(cls, request):
        if wp_settings.WORDPRESS_DEV_USER_ID:
            # We are overriding the normal auth process for dev only
            assert settings.DEBUG, "you can only set WORDPRESS_DEV_USER_ID in DEBUG mode"

            return cls.objects.get(id=wp_settings.WORDPRESS_DEV_USER_ID)

        if wp_settings.WORDPRESS_COOKIEHASH is None:
            cookie_hash = hashlib.md5(utils.encoding.force_bytes(WpOptions.get_site_url())
                                ).hexdigest()
        else:
            cookie_hash = wp_settings.WORDPRESS_COOKIEHASH

        cookie = request.COOKIES.get('wordpress_logged_in_' + cookie_hash)

        if cookie:
            cookie = urllib.parse.unquote_plus(cookie)
            cookie = wp_cookie.AuthCookie(cookie)
            
            try:
                wordpress_user = cookie.validate()
            except cookie.ValidationError:
                return auth_models.AnonymousUser()

            return cls.objects.get(id=wordpress_user.id)

        return auth_models.AnonymousUser()

    @classmethod
    def get_from_username(cls, username):
        return cls.objects.get(user_login=username)

    def get_data(self):
        return {meta.meta_key: meta.meta_value for meta in self.get_meta()}

    def get_session_tokens(self):
        meta = self.get_meta()

        tokens = meta.get(meta_key="session_tokens").meta_value

        return phpserialize.loads(utils.encoding.force_bytes(tokens),
                                  decode_strings=True)

    def get_meta(self):
        return WpUsermeta.objects.filter(user_id=self.id)


class WpPostmeta(models.Model):
    meta_id = models.BigAutoField(primary_key=True)
    post_id = models.BigIntegerField()
    meta_key = models.CharField(max_length=255, blank=True, null=True)
    meta_value = models.TextField(blank=True, null=True)

    objects = WordpressManager()

    class Meta:
        managed = False
        db_table = 'wp_postmeta'


class WpPosts(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    post_author = models.BigIntegerField()
    post_date = models.DateTimeField()
    post_date_gmt = models.DateTimeField()
    post_content = models.TextField()
    post_title = models.TextField()
    post_excerpt = models.TextField()
    post_status = models.CharField(max_length=20)
    comment_status = models.CharField(max_length=20)
    ping_status = models.CharField(max_length=20)
    post_password = models.CharField(max_length=255)
    post_name = models.CharField(max_length=200)
    to_ping = models.TextField()
    pinged = models.TextField()
    post_modified = models.DateTimeField()
    post_modified_gmt = models.DateTimeField()
    post_content_filtered = models.TextField()
    post_parent = models.BigIntegerField()
    guid = models.CharField(max_length=255)
    menu_order = models.IntegerField()
    post_type = models.CharField(max_length=20)
    post_mime_type = models.CharField(max_length=100)
    comment_count = models.BigIntegerField()

    objects = WordpressManager()

    class Meta:
        managed = False
        db_table = 'wp_posts'

    def get_data(self):
        return {meta.meta_key: meta.meta_value for meta in self.get_meta()}

    def get_meta(self):
        return WpPostmeta.objects.filter(post_id=self.id)
