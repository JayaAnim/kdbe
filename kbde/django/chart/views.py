from django import views

from kbde import json as kbde_json
import json


class Chart(views.generic.ListView):
    chart_type = None
    
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data["chart_id"] = self.get_chart_id(context_data)
        context_data["chart"] = json.dumps(self.get_chart(context_data), cls=kbde_json.Encoder)

        return context_data

    def get_chart(self, context_data):
        chart = {
            "type": self.get_chart_type(context_data),
            "data": self.get_chart_data(context_data),
            "options": self.get_chart_options(context_data),
            }
        return chart

    def get_chart_id(self, context_data):
        return 0

    def get_chart_type(self, context_data):
        assert self.chart_type, f"{self.__class__.__name__} must define `chart_type`"
        return self.chart_type

    def get_chart_data(self, context_data):
        data = {
            "datasets": list(self.get_chart_datasets(context_data)),
            "labels": list(self.get_chart_labels(context_data)),
            }
        return data

    def get_chart_options(self, context_data):
        return {
            "scales": {
                "yAxes": [
                    {
                        "ticks": {
                            "beginAtZero": True,
                            },
                        },
                    ],
                },
            }

    def get_chart_datasets(self, context_data):
        raise NotImplementedError(f"{self.__class__.__name__} must implement `get_chart_datasets()`")

    def get_chart_labels(self, context_data):
        raise NotImplementedError(f"{self.__class__.__name__} must implement `get_chart_labels()`")
