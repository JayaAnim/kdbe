from kbde.django import views as kbde_views


class Modal(kbde_views.TemplateView):
    template_name = "kbde/django/bootstrap/partials/Modal.html"
    modal_button_text = None
    modal_show = False

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data.update({
            "modal_button_text": self.get_modal_button_text(),
            "modal_show": self.get_modal_show()
        })

        return context_data

    def get_modal_button_text(self):
        assert self.modal_button_text is not None, (
            f"{self.__class__} must define .modal_button_text or override "
            f".get_modal_button_text()"
        )
        return self.modal_button_text

    def get_modal_show(self):
        return self.kwargs.get(
            "modal_show",
            self.modal_show,
        )


class JsTabs(kbde_views.TemplateView):
    template_name = "kbde/django/bootstrap/partials/JsTabs.html"
    tab_partials = None
    show_tabs = True

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()

        context_data.update({
            "tab_partials": self.get_tab_partials(),
            "show_tabs": self.get_show_tabs(),
        })

        return context_data

    def get_tab_partials(self):
        assert self.tab_partials is not None, (
            f"{self.__class__} must define .tab_partials, as a list of pairs: "
            f"('Tab Title', 'template/path/to/partial.html')"
        )
        return self.tab_partials

    def get_show_tabs(self):
        return self.show_tabs
