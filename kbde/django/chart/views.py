from django import views

from . import mixins


class Chart(mixins.Chart, views.generic.TemplateView):
    """
    Renders a chart into a template
    """


class ListChart(mixins.Queryset, views.generic.ListView):
    """
    Renders a chart from a listview
    """
