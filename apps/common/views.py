from django.shortcuts import render,redirect
from apps.common.models import Usuario, ProdutoTipo, Produto
from apps.common.carrinho import get_carrinho_dict, save_carrinho_dict
from django.http import HttpRequest, HttpResponse
import json

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

def carrinho_editar(request:HttpRequest, id, quantidade) -> HttpResponse:
    carrinho = get_carrinho_dict(request)
    carrinho[id] = quantidade
    resp = HttpResponse(json.dumps(carrinho))
    save_carrinho_dict(resp, carrinho)
    return resp

def carrinho_deletar(request:HttpRequest, id) -> HttpResponse:
    carrinho = get_carrinho_dict(request)
    del carrinho[id]
    resp = HttpResponse(json.dumps(carrinho))
    save_carrinho_dict(resp, carrinho)
    return resp

def carrinho_carregar(request:HttpRequest) -> HttpResponse:
    return HttpResponse(json.dumps(get_carrinho_dict(request)))


def cardapio(request):
    tipos_produtos = ProdutoTipo.objects.all()
    tipo_selecionado = request.GET.get("tipo")
    if not tipo_selecionado:
        tipo_ativo = ProdutoTipo.objects.get(tipo="Pizzas Salgadas")
        produtos = Produto.objects.filter(idtipo=tipo_ativo)
    else:
        tipo_ativo = ProdutoTipo.objects.get(id=tipo_selecionado)
        produtos = Produto.objects.filter(idtipo=tipo_ativo)
    return render(request, 'painel.html', context={'view': 'cardapio.html', 'title': 'Cardápio', 'tipos': tipos_produtos, "tipo_ativo": tipo_ativo, 'produtos': produtos})

def pedidos(request):
    return render(request, 'painel.html', context={'view': 'pedidos.html', 'title': 'Pedidos'})