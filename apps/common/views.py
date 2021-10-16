from django.shortcuts import render,redirect, get_list_or_404
from apps.common.models import Usuario, ProdutoTipo, Produto
from django.http import HttpRequest, HttpResponse
from django.core import serializers

# Create your views here.
def index(request:HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('painel')
    else:
        return redirect('login')

def painel(request:HttpRequest) -> HttpResponse:
    return render(request, 'painel.html', context={'view': 'pedidos.html', 'title': 'Pedidos'})

def clientes(request:HttpRequest) -> HttpResponse:
    usuarios = Usuario.objects.all()
    return render(request, 'painel.html', context={'view': 'clientes.html', 'title': 'Clientes', 'usuarios': usuarios})

def clientes_delete(request:HttpRequest, email) -> HttpResponse:
    Usuario.objects.filter(email=email).delete()
    return clientes(request)

def clientes_cadastro(request:HttpRequest) -> HttpResponse:
    return render(request, 'painel.html', context={'view': 'clientes_cadastro.html', 'title': 'Cadastrar cliente'})

def clientes_inserir(request:HttpRequest):
    return True

def cardapio(request:HttpRequest) -> HttpResponse:
    tipos_produtos = ProdutoTipo.objects.all()
    tipo_selecionado = request.GET.get("tipo")
    if not tipo_selecionado:
        tipo_ativo = ProdutoTipo.objects.get(tipo="Pizzas Salgadas")
    else:
        tipo_ativo = ProdutoTipo.objects.get(id=tipo_selecionado)
    return render(request, 'painel.html', context={'view': 'cardapio.html', 'title': 'Cardápio', 'tipos': tipos_produtos, "tipo_ativo": tipo_ativo})

def cardapio_categoria(request:HttpRequest) -> HttpResponse:
    tipo_desejado = request.GET.get("tipo")
    tipo = ProdutoTipo.objects.get(id=tipo_desejado)
    return HttpResponse(serializers.serialize('json', (get_list_or_404(Produto, idtipo=tipo))))

def pedidos(request:HttpRequest) -> HttpResponse:
    return render(request, 'painel.html', context={'view': 'pedidos.html', 'title': 'Pedidos'})