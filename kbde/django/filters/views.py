from django_filters import views as filter_views
from kbde.django import views as kbde_views
from kbde.django.json_views import views as json_views


class FiltersetMixin(kbde_views.PostToGetMixin, filter_views.FilterMixin):
    model = None
    queryset = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filterset = None

    def get_context_data(self, **kwargs):
        return super().get_context_data(filterset=self.get_filterset())
    
    def get_queryset(self):
        filterset = self.get_filterset()

        if (
            not filterset.is_bound
            or filterset.is_valid()
            or not self.get_strict()
        ):
            queryset = filterset.qs
        else:
            queryset = filterset.queryset.none()

        return queryset

    def get_filterset(self):
        if self.filterset is None:
            self.filterset = super().get_filterset(self.get_filterset_class())

        return self.filterset

    def get_filterset_kwargs(self, filterset_class):
        kwargs = {
            'data': self.request.GET or None,
            'request': self.request,
        }

        if hasattr(super(), "get_queryset"):
            kwargs["queryset"] = super().get_queryset()

        return kwargs


class JsonFiltersetMixin(json_views.FormDescriptionMixin, FiltersetMixin):
    
    def get_response_context(self, context):
        response_context = super().get_response_context(context)

        response_context["filterset"] = self.get_form_description_data(
            self.filterset.form
        )

        return response_context
