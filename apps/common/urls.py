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
    path('clientes/modal/', views.clientes_modal, name='clientes_modal'),
    path('clientes/cadastro', views.clientes_cadastro, name='clientes_cadastro'),
    path('clientes/<int:pk>/dados', views.clientes_dados, name='clientes_dados'),
    path('clientes/<int:pk>', views.clientes_pagina_editar, name='clientes_pagina_editar'),
    path('clientes/editar/', views.clientes_editar, name='clientes_editar'),
    path('clientes/delete/<pk>', views.clientes_delete, name='clientes_delete'),
    path('clientes/inserir', views.clientes_inserir, name='clientes_inserir'),
    path('clientes/busca', views.clientes_busca, name="clientes_busca"),
    path('carrinho/deletar/<id>', views.carrinho_deletar, name='carrinho_deletar'),
    path('carrinho/editar/<id_item>/<id_produto>/<quantidade>', views.carrinho_editar, name='carrinho_editar'),
    path('carrinho/carregar', views.carrinho_carregar, name='carrinho_carregar'),
    path('cardapio/', views.cardapio, name='cardapio'),
    path('cardapio/busca', views.cardapio_busca, name='cardapio_busca'),
    path('cardapio/<cliente_selecionado>', views.cardapio_cliente, name='cardapio_cliente'),
    path('produto', views.buscar_produto, name='buscar_produtos'),
    path('pedidos/novo', views.pedidos_novo, name='pedidos_novo'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('pedidos/carregar/<int:pk>', views.pedidos_carregar, name='pedidos_carregar'),
    path('pedidos/busca', views.pedidos_busca, name='pedidos_busca'),
    path('pedidos/cancelar/', views.pedidos_cancelar, name='pedidos_cancelar'),
    path('pedidos/finalizar/', views.pedidos_finalizar, name='pedidos_finalizar'),
]