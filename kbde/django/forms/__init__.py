from django import forms

from . import widgets
from . import mixins


class SearchForm(forms.Form):
    search = forms.CharField()
