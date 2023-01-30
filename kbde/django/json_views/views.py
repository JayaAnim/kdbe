from django import http, views, forms, shortcuts
from django.conf import settings
from django.core import exceptions
from django.contrib.auth import models as auth_models
from django.views.decorators import csrf
from kbde.django import views as kbde_views
from kbde.django.json import encoder as kbde_encoder

import json


NOT_FOUND = object()


class JsonResponseMixin(kbde_views.UrlPathMixin,
                        kbde_views.PermissionsMixin,
                        views.generic.base.ContextMixin):
    fields = None
    response_class = http.JsonResponse
    response_json_encoder = kbde_encoder.Encoder
    content_type = "application/json"
    child_views = {}
    login_url = None
    unauthenticated_status_code = 401
    request_user_attrs = getattr(
        settings,
        "JSON_REQUEST_USER_ATTRS",
        [
            "token_user",
            "session_header_user",
        ],
    )

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return csrf.csrf_exempt(view)

    def setup(self, request, *args, **kwargs):
        # Ignore the default request.user
        request.user = auth_models.AnonymousUser()

        request_users = [
            getattr(request, attr, None) for attr in self.request_user_attrs
        ]
        request_users = [
            user for user in request_users if user is not None
        ]
        authenticated_request_users = [
            user for user in request_users if user.is_authenticated
        ]

        if authenticated_request_users:
            request.user = authenticated_request_users[0]

        self.set_request_data(request)

        return super().setup(request, *args, **kwargs)

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)

        # If the response is trying to redirect the user to the login page,
        # return an "unauthenticated_status_code" instead
        if (
            isinstance(response, http.HttpResponseRedirect)
            and response.url.startswith(self.get_login_url())
        ):
            return self.render_to_response(
                None,
                status=self.unauthenticated_status_code,
            )

        return response

    def get_login_url(self):
        login_url = self.login_url or settings.LOGIN_URL
        assert login_url, (
            f"{self.__class__} must define .login_url, or you must define "
            f"LOGIN_URL in your settings"
        )
        return shortcuts.resolve_url(login_url)

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault("content_type", self.content_type)
        response_kwargs.setdefault("encoder", self.response_json_encoder)

        if context is not None:
            response_context = self.get_response_context(context)
        else:
            response_context = {}

        return self.response_class(response_context, **response_kwargs)
        
    def get_response_context(self, context):
        """
        Creates a response context, which defines shape of the response data
        """
        return {
            "data": self.get_response_data(context),
        }

    def get_response_data(self, context):
        """
        Returns the data which will go in the response's `data` field
        Gets object data, then renders all child views
        """
        if context is None:
            return None

        object_data = self.get_object_data(context)
        return self.process_child_views(object_data)
        
    def get_object_data(self, context):
        return {
            field_name: context[field_name] for
            field_name in self.get_fields()
        }

    def get_fields(self):
        assert self.fields is not None, (
            f"{self.__class__} must define .fields or override "
            f".get_fields()"
        )
        return self.fields

    def process_child_views(self, object_data):
        child_views = self.get_child_views()

        for field_name, view_class in child_views.items():
            view = view_class()
            view.request = self.request

            value = object_data[field_name]

            object_data[field_name] = view.get_response_data(value)

        return object_data

    def get_child_views(self):
        return self.child_views.copy()

    def set_request_data(self, request):
        content_type = request.headers.get("content-type")

        if (
            content_type
            and content_type.lower() == "application/json"
            and request.body
        ):
            request.POST = self.get_json_request_data(request)

        return request

    def get_json_request_data(self, request):
        try:
            data = json.loads(request.body.decode("latin1"))
        except ValueError:
            raise exceptions.SuspiciousOperation(
                "The payload was not valid JSON"
            )

        if not isinstance(data, dict):
            raise exceptions.SuspiciousOperation(
                "The payload must be a JSON object"
            )

        return data


class JsonView(JsonResponseMixin, views.generic.View):

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class SingleObjectMixin:
    
    def get_response_context(self, context):
        return {
            "data": self.get_response_data(context["object"]),
        }

    def get_object_data(self, obj):
        return {
            field_name: self.get_value_from_object(obj, field_name)
            for field_name in self.get_fields()
        }

    def get_value_from_object(self, obj, field):
        # Try to get with a getter method
        get_method_name = f"get_{field}"

        # Try to use the getter method on this class
        get_method = getattr(self, get_method_name, NOT_FOUND)

        if get_method != NOT_FOUND:
            return get_method(obj)

        # Try to use the getter method on the object
        obj_get_method = getattr(obj, get_method_name, NOT_FOUND)

        if obj_get_method != NOT_FOUND:
            return obj_get_method()

        # Get explicit value from the object
        explicit_value = getattr(obj, field, NOT_FOUND)

        if explicit_value != NOT_FOUND:
            return explicit_value

        assert False, (
            f"Could not get value for field `{field}` on object `{obj}`"
        )


class DetailView(SingleObjectMixin,
                 JsonResponseMixin,
                 kbde_views.UserAllowedQuerysetMixin,
                 views.generic.DetailView):

    def get_queryset(self):
        return self.get_user_read_queryset()


class RenderDetailMixin:
    detail_view_class = None

    def render_detail_view(self, context):
        detail_view = self.get_detail_view()
        return detail_view.get_response_data(context)

    def get_detail_view(self):
        detail_view_class = self.get_detail_view_class()
        detail_view = detail_view_class(**self.get_detail_view_kwargs())
        detail_view.request = self.request
        return detail_view

    def get_detail_view_class(self):
        assert self.detail_view_class is not None, (
            f"{self.__class__} must define .detail_view_class or override "
            f"self.get_detail_view_class()"
        )
        return self.detail_view_class

    def get_detail_view_kwargs(self):
        return {}


class ListView(RenderDetailMixin,
               JsonResponseMixin,
               kbde_views.UserAllowedQuerysetMixin,
               views.generic.ListView):

    def get_queryset(self):
        queryset = self.get_user_read_queryset()

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_response_context(self, context):
        response_context = {
            "data": self.get_response_data(context["object_list"]),
        }

        response_context.update(self.get_pagination_data(context))
        
        return response_context

    def get_object_data(self, object_list):
        detail_view = self.get_detail_view()

        return [
            self.render_detail_view(obj)
            for obj in object_list
        ]

    def get_pagination_data(self, context):
        paginator = context.get("paginator")

        if not paginator:
            return {
                "count": len(context["object_list"])
            }

        page_obj = context["page_obj"]

        return {
            "count": paginator.count,
            "page_count": paginator.num_pages,
            "page": page_obj.number,
        }


class FormMixin(RenderDetailMixin):
    form_error_status_code = 422
    form_success_status_code = 200

    def form_valid(self, form):
        super().form_valid(form)

        context = {
            "form": form,
        }

        return self.render_to_response(
            context,
            status=self.form_success_status_code,
        )

    def render_to_response(self, context, **response_kwargs):
        if context is not None:
            form = context.get("form")

            if form and form.errors:
                response_kwargs["status"] = self.form_error_status_code

        return super().render_to_response(context, **response_kwargs)

    def get_response_context(self, context):
        form = context["form"]
        response_context = {}

        if hasattr(form, "cleaned_data") and not form.errors:
            response_context["data"] = self.render_detail_view(form.cleaned_data)
        else:
            response_context["form"] = form

        return response_context

    def get_success_url(self):
        return ""


class FormView(FormMixin, JsonResponseMixin, views.generic.FormView):
    pass


class ModelFormMixin(FormMixin):

    def render_detail_view(self, cleaned_data):
        return super().render_detail_view(self.object)


class CreateView(ModelFormMixin, JsonResponseMixin, views.generic.CreateView):
    form_success_status_code = 201


class UpdateView(ModelFormMixin,
                 JsonResponseMixin,
                 kbde_views.UserAllowedQuerysetMixin,
                 views.generic.UpdateView):

    def get_queryset(self):
        return self.get_user_update_queryset()


class DeleteView(SingleObjectMixin,
                 JsonResponseMixin,
                 kbde_views.UserAllowedQuerysetMixin,
                 views.generic.DeleteView):
    delete_success_status_code = 200

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        return self.render_to_response(
            None,
            status=self.delete_success_status_code,
        )

    def get_queryset(self):
        return self.get_user_delete_queryset()

    def get_success_url(self):
        return ""
