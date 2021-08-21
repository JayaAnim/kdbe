from django import http, views, forms
from django.views.decorators import csrf
from kbde.django.views import mixins as kbde_mixins

from collections import abc


no_object = object()


class JsonResponseMixin(kbde_mixins.UrlPath, views.generic.base.ContextMixin):
    fields = None
    response_class = http.JsonResponse
    content_type = "application/json"
    child_views = {}

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return csrf.csrf_exempt(view)

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault('content_type', self.content_type)

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
            value = object_data[field_name]
            object_data[field_name] = view.get_response_data(value)

        return object_data

    def get_child_views(self):
        return self.child_views


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
            field_name: getattr(obj, field_name)
            for field_name in self.get_fields()
        }


class DetailView(SingleObjectMixin, JsonResponseMixin, views.generic.DetailView):
    pass


class RenderDetailMixin:
    detail_view_class = None

    def render_detail_view(self, context):
        detail_view = self.get_detail_view()
        return detail_view.get_response_data(context)

    def get_detail_view(self):
        detail_view_class = self.get_detail_view_class()
        return detail_view_class(**self.get_detail_view_kwargs())

    def get_detail_view_class(self):
        assert self.detail_view_class is not None, (
            f"{self.__class__} must define .detail_view_class or override "
            f"self.get_detail_view_class()"
        )
        return self.detail_view_class

    def get_detail_view_kwargs(self):
        return {}


class ListView(RenderDetailMixin, JsonResponseMixin, views.generic.ListView):

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
    all_field_attrs = [
        "required",
        "label",
        "label_suffix",
        "initial",
        "help_text",
        "localize",
        "disabled",
    ]

    field_attr_map = {
        forms.CharField: [
            "min_length",
            "max_length",
            "empty_value",
        ],
        forms.ChoiceField: [
            "choices",
        ],
        forms.TypedChoiceField: [
            "choices"
            "empty_value",
        ],
        forms.DateField: [
            "input_formats",
        ],
        forms.DateTimeField: [
            "input_formats",
        ],
        forms.DecimalField: [
            "min_value",
            "max_value",
            "max_digits",
            "decimal_places",
        ],
        forms.IntegerField: [
            "min_value",
            "max_value",
        ],
    }

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
        if context["form"].errors:
            response_kwargs["status"] = self.form_error_status_code

        return super().render_to_response(context, **response_kwargs)

    def get_response_context(self, context):
        form = context["form"]
        response_context = {}

        if form.errors:
            response_context["errors"] = form.errors

        if hasattr(form, "cleaned_data") and not form.errors:
            response_context["data"] = self.render_detail_view(form.cleaned_data)
        else:
            response_context["data"] = self.get_form_data(form)
            response_context["form"] = self.get_form_description_data(form)

        return response_context

    def get_form_description_data(self, form):
        all_field_attrs = self.get_all_field_attrs()
        field_attr_map = self.get_field_attr_map()
        description_data = {}

        for field_name in form.fields:
            bound_field = form[field_name]
            field_attrs = field_attr_map.get(bound_field.field.__class__, [])
            description_data[field_name] = self.get_field_description_data(
                bound_field.field,
                all_field_attrs + field_attrs,
            )

        return description_data

    def get_field_description_data(self, field, attrs):
        description_data = {}
        for field_attr in attrs:
            if not hasattr(field, field_attr):
                continue

            value = getattr(field, field_attr)

            if not isinstance(value, str) and isinstance(value, abc.Iterable):
                value = list(value)

            description_data[field_attr] = value

        return description_data

    def get_form_data(self, form):
        return {
            field_name: form[field_name].value()
            for field_name in form.fields
        }

    def get_all_field_attrs(self):
        return self.all_field_attrs

    def get_field_attr_map(self):
        return self.field_attr_map

    def get_success_url(self):
        return ""


class FormView(FormMixin, JsonResponseMixin, views.generic.FormView):
    pass


class ModelFormMixin(FormMixin):

    def render_detail_view(self, cleaned_data):
        return super().render_detail_view(self.object)


class CreateView(ModelFormMixin, JsonResponseMixin, views.generic.CreateView):
    form_success_status_code = 201


class UpdateView(ModelFormMixin, JsonResponseMixin, views.generic.UpdateView):
    pass


class DeleteView(SingleObjectMixin, JsonResponseMixin, views.generic.DeleteView):
    delete_success_status_code = 200

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        return self.render_to_response(
            None,
            status=self.delete_success_status_code,
        )

    def get_success_url(self):
        return ""
