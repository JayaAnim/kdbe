from django import views

from . import mixins


class View(mixins.Base, views.generic.View):
    pass


class TemplateView(mixins.Base, mixins.PostToGet, views.generic.TemplateView):
    pass


class RedirectView(mixins.Base, views.generic.RedirectView):
    pass


class DetailView(mixins.Base, mixins.PostToGet, views.generic.DetailView):
    pass


class ListView(mixins.Base, mixins.PostToGet, views.generic.ListView):
    pass


class FormView(mixins.Base, views.generic.FormView):
    pass


class CreateView(mixins.Base, views.generic.CreateView):
    pass


class UpdateView(mixins.Base, views.generic.UpdateView):
    pass


class DeleteView(mixins.Base, views.generic.DeleteView):
    pass
