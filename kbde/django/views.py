from django import views

from . import mixins


class View(mixins.Base, views.generic.View):
    pass


class TemplateView(mixins.Base, mixins.PostToGet, views.generic.TemplateView):
    pass


class RedirectView(mixins.Base, views.generic.RedirectView):
    pass


class DetailView(mixins.Base,
                 mixins.PostToGet,
                 mixins.UserAllowedInstances,
                 views.generic.DetailView):

    def get_queryset(self):
        return self.get_user_read_instances()


class ListView(mixins.Base,
               mixins.PostToGet,
               mixins.UserAllowedInstances,
               views.generic.ListView):

    def get_queryset(self):
        queryset = self.get_user_read_instances()

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset


class FormView(mixins.Base, views.generic.FormView):
    pass


class CreateView(mixins.Base, views.generic.CreateView):
    pass


class UpdateView(mixins.Base,
                 mixins.UserAllowedInstances,
                 views.generic.UpdateView):

    def get_queryset(self):
        return self.get_user_update_instances()


class DeleteView(mixins.Base,
                 mixins.UserAllowedInstances,
                 views.generic.DeleteView):

    def get_queryset(self):
        return self.get_user_delete_instances()
