from django import views, template, utils
from django.contrib.auth import views as auth_views

from . import mixins


class View(mixins.Base, views.generic.View):
    pass


class TemplateView(mixins.PostToGet, mixins.Base, views.generic.TemplateView):
    pass


class RedirectView(mixins.Base, views.generic.RedirectView):
    pass


class DetailView(mixins.PostToGet,
                 mixins.UserAllowedQueryset,
                 mixins.Base,
                 views.generic.DetailView):

    def get_queryset(self):
        return self.get_user_read_queryset()


class ListView(mixins.PostToGet,
               mixins.UserAllowedQueryset,
               mixins.Base,
               views.generic.ListView):

    def get_queryset(self):
        queryset = self.get_user_read_queryset()

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset


class FormView(mixins.Form, mixins.Base, views.generic.FormView):
    pass


class CreateView(mixins.Form, mixins.Base, views.generic.CreateView):
    pass


class UpdateView(mixins.Form,
                 mixins.UserAllowedQueryset,
                 mixins.Base,
                 views.generic.UpdateView):

    def get_queryset(self):
        return self.get_user_update_queryset()


class DeleteView(mixins.UserAllowedQueryset,
                 mixins.Base,
                 views.generic.DeleteView):

    def get_queryset(self):
        return self.get_user_delete_queryset()


# Auth


class LoginView(mixins.Form, mixins.Base, auth_views.LoginView):
    permission_classes = []


# Custom Views


class MarkdownView(TemplateView):
    """
    A component view which renders a markdown_template into HTML
    """
    template_name = "kbde/MarkdownView.html"
    markdown_template_name = None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["markdown"] = self.get_markdown(context_data)
        return context_data

    def get_markdown(self, context_data):
        import markdown

        markdown_template_name = self.get_markdown_template_name()
        markdown_content = template.loader.render_to_string(
            markdown_template_name,
            context_data,
        )

        html = markdown.markdown(markdown_content)

        return utils.safestring.mark_safe(html)

    def get_markdown_template_name(self):
        return (
            self.markdown_template_name or 
            self.get_class_template_name(file_extension="md")
        )
