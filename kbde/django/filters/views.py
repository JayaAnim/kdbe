from django.core import exceptions
from django_filters import views as filter_views
from kbde.django import views as kbde_views
from kbde.django.json_views import views as json_views


class FiltersetMixin(kbde_views.PostToGetMixin, filter_views.FilterMixin):
    model = None
    queryset = None

    def get(self, *args, **kwargs):
        self.filterset = self.get_filterset(self.get_filterset_class())
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()

        context_data["filterset"] = self.filterset

        return context_data
    
    def get_queryset(self):
        queryset = super().get_queryset()

        if (
            not self.filterset.is_bound
            or self.filterset.is_valid()
            or not self.get_strict()
        ):
            filter_qs = self.filterset.qs
        else:
            filter_qs = self.filterset.queryset.none()

        queryset = queryset.filter(
            pk__in=filter_qs.values_list("pk", flat=True)
        )
        
        if filter_qs.query.order_by:
            queryset = queryset.order_by(*filter_qs.query.order_by)

        return queryset

    def get_filterset_kwargs(self, filterset_class):
        kwargs = {
            'data': self.request.GET or None,
            'request': self.request,
        }

        if filterset_class._meta.model is None:
            kwargs["queryset"] = self.get_filterset_queryset()

        return kwargs

    def get_filterset_queryset(self):
        if self.queryset is not None:
            return self.queryset.all()

        if self.model:
            return self.model._default_manager.all()

        raise exceptions.ImproperlyConfigured(
            f"{self.__class__} must define .queryset, .model, or override "
            f".get_filterset_queryset()"
        )


class JsonFiltersetMixin(json_views.FormDescriptionMixin, FiltersetMixin):
    
    def get_response_context(self, context):
        response_context = super().get_response_context(context)

        response_context["filterset"] = self.get_form_description_data(self.filterset.form)

        return response_context
