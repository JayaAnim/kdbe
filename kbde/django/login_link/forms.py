from django import forms, utils
from django.contrib import auth
from django.contrib.auth import forms as auth_forms
from django.core import exceptions

from . import models


UserModel = auth.get_user_model()


class LoginLinkCreate(forms.ModelForm):
    username = auth_forms.UsernameField(widget=forms.TextInput(attrs={'autofocus': True}))

    does_not_exist_error = "User not found"
    
    class Meta:
        model = models.LoginLink
        fields = [
            "username",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
		# Set the max length and label for the "username" field.
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        username_max_length = self.username_field.max_length or 254
        self.fields['username'].max_length = username_max_length
        self.fields['username'].widget.attrs['maxlength'] = username_max_length
        if self.fields['username'].label is None:
            self.fields['username'].label = utils.text.capfirst(self.username_field.verbose_name)

    def clean(self):
        super().clean()

        if self.errors: 
            return None

        # Get the user
        try:
            self.user = UserModel._default_manager.get_by_natural_key(self.cleaned_data["username"])
        except UserModel.DoesNotExist:
            raise exceptions.ValidationError({"username": self.does_not_exist_error})

    def save(self):
        self.instance.user = self.user
        self.instance.save()

        return self.instance


class LoginLinkAuthenticate(forms.Form):

    user_inactive_error = "The account is inactive"
    
    def __init__(self, instance, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.instance = instance
        self.request = request

    def clean(self):
        if self.instance.confirmed is None:
            # This login link has not been confirmed
            # Raise validation error
            raise exceptions.ValidationError("Link not confirmed")

        if self.instance.confirmed == False:
            # This login link has been declined by the user
            raise exceptions.ValidationError("This link is invalid")

        if self.instance.confirmed:
            # Validate that the user can log in
            if not self.instance.user.is_active:
                raise exceptions.ValidationError(self.user_inactive_error)

    def save(self):
        auth.login(self.request, self.instance.user)
