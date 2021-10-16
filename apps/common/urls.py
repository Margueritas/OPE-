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
    path('clientes/cadastro', views.clientes_cadastro, name='clientes_cadastro'),
    path('clientes/delete/<email>', views.clientes_delete, name='clientes_delete'),
    path('clientes/inserir', views.clientes_inserir, name='clientes_inserir'),
    path('cardapio/', views.cardapio, name='cardapio'),
    path('cardapio/categoria', views.cardapio_categoria, name='cardapio_categoria'),
    path('pedidos/', views.pedidos, name='pedidos'),
]