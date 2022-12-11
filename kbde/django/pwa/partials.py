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


class UserAgentBrowserMixin:
    # auto_install_browsers lists the browser names that will be
    # supported by the InstallButton. These do not require special steps by the user,
    # and they will be guided through the install process automatically
    auto_install_browsers = [
        "Chrome",
        "Chrome Mobile",
    ]
    
    def dispatch(self, *args, **kwargs):
        self.user_agent = self.get_user_agent()
        return super().dispatch(*args, **kwargs)
        
    def get_user_agent(self):
        return user_agents.parse(self.request.META.get('HTTP_USER_AGENT', ''))

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data.update({
            "user_agent": self.user_agent,
            "browser_name": self.get_browser_name(),
            "is_auto_install_browser": self.get_is_auto_install_browser(),
        })

        return context_data

    def get_is_auto_install_browser(self):
        return self.get_browser_name() in self.get_auto_install_browsers()

    def get_browser_name(self):
        return self.user_agent.browser.family

    def get_auto_install_browsers(self):
        return self.auto_install_browsers.copy()


class InstallButton(UserAgentBrowserMixin, views.ManifestMixin, kbde_views.TemplateView):
    template_name = "kbde/django/pwa/partials/InstallButton.html"
    install_button_text = "Install App"
    no_auto_install_message = "This app cannot be installed automatically"
    already_installed_message = "The app is already installed on this device"
    permission_classes = []

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data.update({
            "install_button_text": self.get_install_button_text(),
            "no_auto_install_message": self.get_no_auto_install_message(),
            "already_installed_message": self.get_already_installed_message(),
        })

        return context_data

    def get_install_button_text(self):
        return self.install_button_text

    def get_no_auto_install_message(self):
        return self.no_auto_install_message

    def get_already_installed_message(self):
        return self.already_installed_message


class InstallInstructions(UserAgentBrowserMixin, kbde_views.MarkdownView):
    markdown_template_name = "kbde/django/pwa/partials/InstallInstructions.md"
    auto_install_template_name = "kbde/django/pwa/partials/auto_install.md"

    # instruction_template_names should be a mapping between browser names that
    # require special installation steps by the user, which cannot be guided
    # via InstallButton
    instruction_template_names = {
        "Mobile Safari": "kbde/django/pwa/partials/install_mobile_safari.md",
    }
    unsupported_template_name = (
        "kbde/django/pwa/partials/unsupported_browser.md"
    )

    permission_classes = []

    def get_markdown(self, context_data):
        context_data.update({
            "instruction_template_name": self.get_instruction_template_name(),
            "user_agent": self.user_agent,
            "browser_name": self.get_browser_name(),
        })

        return super().get_markdown(context_data)

    def get_instruction_template_name(self):
        if self.get_is_auto_install_browser():
            return self.get_auto_install_template_name()

        browser_name = self.get_browser_name()
        instruction_template_names = self.get_instruction_template_names()

        instruction_template_name = instruction_template_names.get(browser_name)

        if instruction_template_name is not None:
            return instruction_template_name

        return self.get_unsupported_template_name()

    def get_auto_install_template_name(self):
        return self.auto_install_template_name

    def get_instruction_template_names(self):
        return self.instruction_template_names.copy()

    def get_unsupported_template_name(self):
        return self.unsupported_template_name

    def get_unsupported_browser_url(self):
        return self.unsupported_browser_url


class Installer(UserAgentBrowserMixin, kbde_views.TemplateView):
    template_name = "kbde/django/pwa/partials/Installer.html"
    permission_classes = []
