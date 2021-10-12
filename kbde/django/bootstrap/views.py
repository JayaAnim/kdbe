from kbde.django import views as kbde_views


class ModalView(kbde_views.TemplateView):
    template_name = "kbde/ModalView.html"
    modal_button_text = None
    default_modal_button_class = "btn btn-primary"
    modal_header_text = None
    modal_body_template_name = None
    modal_show = False

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data.update({
            "modal_button_text": self.get_modal_button_text(),
            "modal_button_class": self.get_modal_button_class(),
            "modal_header_text": self.get_modal_header_text(),
            "modal_body_template_name": self.get_modal_body_template_name(),
            "modal_show": self.get_modal_show()
        })

        return context_data

    def get_modal_button_text(self):
        assert self.modal_button_text is not None, (
            f"{self.__class__} must define .modal_button_text or override "
            f".get_modal_button_text()"
        )
        return self.modal_button_text

    def get_modal_button_class(self):
        return self.kwargs.get(
            "modal_button_class",
            self.default_modal_button_class,
        )

    def get_modal_header_text(self):
        assert self.modal_header_text is not None, (
            f"{self.__class__} must define .modal_header_text or "
            f"override .get_modal_header_text()"
        )
        return self.modal_header_text

    def get_modal_body_template_name(self):
        assert self.modal_body_template_name is not None, (
            f"{self.__class__} must define .modal_body_template_name or "
            f"override .get_modal_body_template_name()"
        )
        return self.modal_body_template_name

    def get_modal_show(self):
        return self.kwargs.get(
            "modal_show",
            self.modal_show,
        )
