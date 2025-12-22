
from django.views.generic import TemplateView


class GeneratePasswordView(TemplateView):
    template_name = 'menu/generate_password.html'


class SocialSecurityView(TemplateView):
    template_name = 'menu/social_security.html'


class ScummersView(TemplateView):
    template_name = 'menu/scummers.html'


class VirusesView(TemplateView):
    template_name = 'menu/viruses.html'


class VirView(TemplateView):
    template_name = 'menu/vir.html'

class VirInfo(TemplateView):
    template_name = 'menu/virus-info.html'

class BackUpInfo(TemplateView):
    template_name = 'menu/backup-info.html'

