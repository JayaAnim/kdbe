from kbde.django import views as kbde_views

from . import views


try:
    import user_agents
except ImportError:
    assert False, (
        "The user_agents library must be installed: "
        "https://github.com/selwin/python-user-agents"
    )


class Meta(views.ManifestMixin, kbde_views.TemplateView):
    page_template_name = "kbde/django/pwa/views/Meta.html"
    permission_classes = []


class Installer(kbde_views.MarkdownView):
    template_name = "kbde/django/pwa/partials/Installer.html"
    permission_classes = []

    # auto_install_browsers should list the browser names that will be
    # supported by Install.js. These do not require special steps by the user,
    # and they will be guided through the install process automatically
    auto_install_browsers = [
        "Chrome",
        "Chrome Mobile",
    ]
    auto_install_template_name = "kbde/django/pwa/partials/auto_install.md"

    # instruction_template_names should be a mapping between browser names that
    # require special installation steps by the user, which cannot be guided
    # via Install.js
    instruction_template_names = {
    }

    # This url will be displayed when the given browser is not
    # auto-installable, and is not one of the instruction browsers. Users 
    # will be referred to an external resource about PWAs
    unsupported_browser_url = (
        "https://mobilesyrup.com/2020/05/24/"
        "how-install-progressive-web-app-pwa-android-ios-pc-mac/"
    )
    unsupported_template_name = (
        "kbde/django/pwa/partials/unsupported_browser.md"
    )

    def dispatch(self, *args, **kwargs):
        self.user_agent = self.get_user_agent()
        print(self.user_agent.browser.family)
        return super().dispatch(*args, **kwargs)
        
    def get_user_agent(self):
        return user_agents.parse(self.request.META.get('HTTP_USER_AGENT', ''))

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            user_agent=self.user_agent,
            unsupported_browser_url=self.get_unsupported_browser_url(),
            **kwargs,
        )

    def get_unsupported_browser_url(self):
        return self.unsupported_browser_url

    def get_markdown_template_name(self):
        # Check to see if the browser is auto-installable
        if self.user_agent.browser.family in self.get_auto_install_browsers():
            return self.get_auto_install_template_name()

        # Check to see if the browser has supported manual instructions
        instruction_template_name = (
            self.get_instruction_template_names().get(
                self.user_agent.browser.family
            )
        )
        if instruction_template_name is not None:
            return instruction_template_name

        # The browser is not supported by this installer
        return self.get_unsupported_template_name()

    def get_auto_install_browsers(self):
        return self.auto_install_browsers.copy()

    def get_auto_install_template_name(self):
        return self.auto_install_template_name

    def get_instruction_template_names(self):
        return self.instruction_template_names.copy()

    def get_unsupported_template_name(self):
        return self.unsupported_template_name
