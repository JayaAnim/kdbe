from kbde.django import views


class Navbar(views.TemplateView):
    template_name = "coreui/Navbar.html"
    brand_text = None
    brand_image = None
    brand_url = None
    left_items = None
    right_items = None

    def get_brand_text(self):
        return self.brand_text

    def get_brand_image(self):
        return self.brand_image

    def get_brand_url(self):
        assert self.brand_url is not None, (
            f"{self.__class__} must define .brand_url or override "
            f".get_brand_url()"
        )

    def get_left_items(self):
        """
        Returns navbar items.
        In the form of (title, url)
        """
        assert self.left_items is not None, (
            f"{self.__class__} must define .left_items or override "
            f".get_left_items()"
        )
        for title, url in self.left_items:
            yield title, url

    def get_right_items(self):
        assert self.right_items is not None, (
            f"{self.__class__} must define .right_items or override "
            f".get_right_items()"
        )
        for title, url in self.right_items:
            yield title, url


class Accordion(views.TemplateView):
    template_name = "coreui/Accordion.html"
    items = None
    flush = False

    def get_items(self):
        assert self.items is not None, (
            f"{self.__class__} must define .items or override .get_items()"
        )
        for title, view_path in self.items:
            yield title, view_path

    def get_flush(self):
        return self.flush


class JsTabs(views.TemplateView):
    template_name = "coreui/JsTabs.html"
    tabs = None

    def get_tabs(self):
        assert self.tabs is not None, (
            f"{self.__class__} must define .tabs or override .get_tabs()"
        )
        for title, view_path in self.tabs:
            yield title, view_path
