from django import views
from . import mixins


class TemplateView(mixins.Base, views.generic.TemplateView):
    pass


class ListView(mixins.Base, views.generic.ListView):
    pass


class DetailView(mixins.Base, views.generic.DetailView):
    pass


class FormView(mixins.Base, mixins.Edit, views.generic.FormView):
    pass


class CreateView(mixins.Base, mixins.Edit, views.generic.CreateView):
    pass


class UpdateView(mixins.Base, mixins.Edit, views.generic.UpdateView):
    pass


class DeleteView(mixins.Base, mixins.Edit, views.generic.DeleteView):
    pass
