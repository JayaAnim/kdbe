from django import http, views, forms
from django.views.decorators import csrf
from kbde.django import mixins as kbde_mixins

from collections import abc


class JsonResponseMixin(kbde_mixins.UrlPath, views.generic.base.ContextMixin):
    response_fields = None
    response_class = http.JsonResponse
    content_type = "application/json"

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return csrf.csrf_exempt(view)

    def render_to_response(self, context, **response_kwargs):
        response_data = self.get_response_data(context)
        response_kwargs.setdefault('content_type', self.content_type)

        return self.response_class(response_data, **response_kwargs)
        
    def get_response_data(self, context):
        return {
            field_name: context[field_name] for
            field_name in self.get_response_fields()
        }

    def get_response_fields(self):
        assert self.response_fields is not None, (
            f"{self.__class__} must define .response_fields or override "
            f".get_response_fields()"
        )
        return self.response_fields


class JsonView(JsonResponseMixin, views.generic.View):

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class SingleObjectMixin:
    
    def get_response_data(self, context):
        return {
            "data": {
                field_name: getattr(context["object"], field_name)
                for field_name in self.get_response_fields()
            }
        }


class DetailView(SingleObjectMixin, JsonResponseMixin, views.generic.DetailView):
    pass


class ListView(JsonResponseMixin, views.generic.ListView):

    def get_response_data(self, context):
        response_fields = self.get_response_fields()
        data = [
            {
                field_name: getattr(obj, field_name) for
                field_name in response_fields
            }
            for obj in context["object_list"]
        ]

        response_data = {
            "data": data,
        }

        response_data.update(self.get_pagination_data(context))
        
        return response_data

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


class FormMixin:
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

    def render_to_response(self, context, **response_kwargs):
        if context["form"].errors:
            response_kwargs["status"] = self.form_error_status_code

        return super().render_to_response(context, **response_kwargs)

    def get_response_data(self, context):
        form = context["form"]
        response_data = {}

        if form.errors:
            response_data["errors"] = form.errors

        response_data["form"] = self.get_form_description_data(form)
        response_data["data"] = self.get_form_data(form)

        return response_data

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


class FormView(FormMixin, JsonResponseMixin, views.generic.FormView):
    pass


class CreateView(FormMixin, JsonResponseMixin, views.generic.CreateView):
    pass


class UpdateView(FormMixin, JsonResponseMixin, views.generic.UpdateView):
    pass


class DeleteView(SingleObjectMixin, JsonResponseMixin, views.generic.DeleteView):
    delete_success_status_code = 200

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        context_data = self.get_context_data(**kwargs)

        return self.render_to_response(
            context_data,
            status=self.delete_success_status_code,
        )
