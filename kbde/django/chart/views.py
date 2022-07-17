from kbde.django import views as kbde_views
from kbde.django.json import encoder as django_encoder

import json


class ChartMixin:
    chart_class = None

    def get_chart_json(self):
        return json.dumps(self.get_chart(), cls=django_encoder.Encoder)
    
    def get_chart(self):
        return self.get_chart_class()(**self.get_chart_kwargs())
        
    def get_chart_kwargs(self):
        return {
            "queryset": self.get_queryset(),
        }

    def get_chart_class(self):
        assert self.chart_class is not None, (
            f"{self.__class__} must define .chart_class"
        )
        return self.chart_class


class ChartView(ChartMixin, kbde_views.ListView):
    template_name = "kbde/django/chart/views/ChartView.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data["chart_json"] = self.get_chart_json()

        return context_data
