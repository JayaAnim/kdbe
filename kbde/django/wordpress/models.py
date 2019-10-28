from django.db import models
from django import utils
from django.utils.six.moves import urllib

from . import wp_settings, cookie as wp_cookie

import hashlib
import phpserialize


class WordpressMixin:
    
    @classmethod
    def get_all(cls):
        return cls.objects.using("wordpress").all()


class WpOptions(WordpressMixin, models.Model):
    option_id = models.BigAutoField(primary_key=True)
    option_name = models.CharField(unique=True, max_length=191)
    option_value = models.TextField()
    autoload = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'wp_options'

    @classmethod
    def get_site_url(cls):
        url = cls.get_all().get(option_name="siteurl").option_value
        return url.rstrip('/\\')

    @classmethod
    def get_login_url(cls):
        return urllib.parse.urljoin(cls.get_site_url(), wp_settings.WORDPRESS_LOGIN_URL)


class WpUsermeta(WordpressMixin, models.Model):
    umeta_id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    meta_key = models.CharField(max_length=255, blank=True, null=True)
    meta_value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wp_usermeta'


class WpUsers(WordpressMixin, models.Model):
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

    class Meta:
        managed = False
        db_table = 'wp_users'

    @classmethod
    def get_from_request(cls, request):
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
                return None

            return cls.get_all().get(id=wordpress_user.id)

    @classmethod
    def get_from_username(cls, username):
        return cls.get_all().get(user_login=username)

    def get_data(self):
        return {meta.meta_key: meta.meta_value for meta in self.get_meta()}

    def get_session_tokens(self):
        meta = self.get_meta()

        tokens = meta.get(meta_key="session_tokens").meta_value

        return phpserialize.loads(utils.encoding.force_bytes(tokens),
                                  decode_strings=True)

    def get_meta(self):
        return WpUsermeta.get_all().filter(user_id=self.id)


class WpPostmeta(WordpressMixin, models.Model):
    meta_id = models.BigAutoField(primary_key=True)
    post_id = models.BigIntegerField()
    meta_key = models.CharField(max_length=255, blank=True, null=True)
    meta_value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wp_postmeta'


class WpPosts(WordpressMixin, models.Model):
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

    class Meta:
        managed = False
        db_table = 'wp_posts'

    def get_data(self):
        return {meta.meta_key: meta.meta_value for meta in self.get_meta()}

    def get_meta(self):
        return WpPostmeta.get_all().filter(post_id=self.id)
