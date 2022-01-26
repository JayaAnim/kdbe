from django import http
from django.template import response as template_response
from kbde.django import views as kbde_views


class TemplateResponse(template_response.TemplateResponse):
    
    def render(self):
        try:
            return super().render()
        except kbde_views.FormView.Redirect as e:
            return http.HttpResponseRedirect(str(e))
