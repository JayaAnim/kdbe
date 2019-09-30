from django.urls import path

from . import views


urlpatterns = [
    path("<uuid:form_slug>/create", views.Create.as_view(), name="form_create"),
    path("<uuid:form_slug>/<uuid:slug>/update", views.Update.as_view(), name="form_update"),
    ]
