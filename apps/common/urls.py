from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
import config.settings as settings

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name="login.html",), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('painel/', views.painel, name='painel'),
    path('clientes/', views.clientes, name='clientes'),
    path('cardapio/', views.cardapio, name='cardapio'),
    path('pedidos/', views.pedidos, name='pedidos'),
]