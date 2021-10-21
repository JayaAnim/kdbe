from django.core import exceptions
from django_filters import views as filter_views


class FilterMixin(filter_views.FilterMixin):
    model = None
    queryset = None

    def get(self, *args, **kwargs):
        self.filterset = self.get_filterset(self.get_filterset_class())
        return super().get(*args, **kwargs)
    
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

        return queryset.filter(pk__in=filter_qs.values_list("pk", flat=True))

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
