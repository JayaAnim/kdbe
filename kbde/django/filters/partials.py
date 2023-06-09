from kbde.django import views as kbde_views

from . import views


class Filter(views.FiltersetMixin, kbde_views.FormView):
    method = "GET"
    submit_button_text = "Apply Filters"

    def get_form(self):
        return self.get_filterset().form
