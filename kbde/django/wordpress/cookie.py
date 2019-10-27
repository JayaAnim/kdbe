from django import utils

from . import models, wp_settings

import time, hmac, hashlib


class AuthCookie:
    def __init__(self, cookie_data):
        self.cookie_data = cookie_data

    def validate(self):
        cookie_elements = self.get_cookie_elements()

        if not cookie_elements:
            raise self.ValidationError("No cookie elements")

        # Unpack the cookie elements
        username, expiration, token, cookie_hmac = cookie_elements

        # Check that the cookie is not expired
        self.check_expiration(expiration)

        # Get the user
        wordpress_user = self.get_wordpress_user(username)

        # Check the password
        self.check_hash(wordpress_user, expiration, token, cookie_hmac)

        # Check the session tokens
        self.check_session_token(wordpress_user, token)

        return wordpress_user

    def get_cookie_elements(self):
        elements = self.cookie_data.split("|")

        if len(elements) != 4:
            # Cookie was not properly formed
            return None

        return elements

    def check_expiration(self, expiration):
        if float(expiration) < time.time():
            raise self.ValidationError("Cookie expired")

    def get_wordpress_user(self, username):
        try:
            return models.WpUsers.get_from_username(username)
        except models.WpUsers.DoesNotExist:
            raise self.ValidationError("User not found")

    def check_hash(self, wordpress_user, expiration, token, cookie_hmac):
        pwd_frag = wordpress_user.user_pass[8:12]
        key_salt = wp_settings.WORDPRESS_LOGGED_IN_KEY + wp_settings.WORDPRESS_LOGGED_IN_SALT
        key_msg = '{}|{}|{}|{}'.format(wordpress_user.user_login, pwd_frag, expiration, token)
        key = hmac.new(utils.encoding.force_bytes(key_salt),
                       utils.encoding.force_bytes(key_msg),
                       digestmod=hashlib.md5
                 ).hexdigest()

        hash_msg = '{}|{}|{}'.format(wordpress_user.user_login, expiration, token)
        hash_final = hmac.new(utils.encoding.force_bytes(key),
                              utils.encoding.force_bytes(hash_msg),
                              digestmod=hashlib.sha256
                        ).hexdigest()

        if hash_final != cookie_hmac:
            raise self.ValidationError("Cookie hash did not match")

    def check_session_token(self, wordpress_user, token):
        verifier = hashlib.sha256(utils.encoding.force_bytes(token)
                         ).hexdigest()
        
        if verifier not in wordpress_user.get_session_tokens():
            raise self.ValidationError("Session token not valid")

    class CookieException(Exception):
        pass

    class ValidationError(CookieException):
        pass
