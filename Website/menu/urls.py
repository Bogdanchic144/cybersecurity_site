
from django.urls import path

from menu import views

app_name = 'menu'

urlpatterns = [
    path(
        'generate_password/',
        views.GeneratePasswordView.as_view(),
        name='generate_password'
    ),

    path(
        'social_security/',
        views.SocialSecurityView.as_view(),
        name='social_security'
    ),

    path(
        'scummers/',
        views.ScummersView.as_view(),
        name='scummers'
    ),

    path(
        'viruses/',
        views.VirusesView.as_view(),
        name='viruses'
    ),

    path( 'vir/', views.VirView.as_view(),
    name = 'vir')
]

