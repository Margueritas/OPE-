from django.shortcuts import render,redirect
from apps.common.models import Usuario, ProdutoTipo, Produto
from django.http import HttpRequest

# Create your views here.
def index(request:HttpRequest):
    if request.user.is_authenticated:
        return redirect('painel')
    else:
        return redirect('login')

def painel(request:HttpRequest):
    return render(request, 'painel.html', context={'view': 'pedidos.html', 'title': 'Pedidos'})

def clientes(request:HttpRequest):
    usuarios = Usuario.objects.all()
    return render(request, 'painel.html', context={'view': 'clientes.html', 'title': 'Clientes', 'usuarios': usuarios})

def clientes_delete(request:HttpRequest, email):
    Usuario.objects.filter(email=email).delete()
    return clientes(request)

def clientes_cadastro(request:HttpRequest):
    return render(request, 'painel.html', context={'view': 'clientes_cadastro.html', 'title': 'Cadastrar cliente'})

def clientes_inserir(request:HttpRequest):
    return True

def cardapio(request:HttpRequest):
    tipos_produtos = ProdutoTipo.objects.all()
    tipo_selecionado = request.GET.get("tipo")
    if not tipo_selecionado:
        tipo_ativo = ProdutoTipo.objects.get(tipo="Pizzas Salgadas")
        produtos = Produto.objects.filter(idtipo=tipo_ativo)
    else:
        tipo_ativo = ProdutoTipo.objects.get(id=tipo_selecionado)
        produtos = Produto.objects.filter(idtipo=tipo_ativo)
    return render(request, 'painel.html', context={'view': 'cardapio.html', 'title': 'Cardápio', 'tipos': tipos_produtos, "tipo_ativo": tipo_ativo, 'produtos': produtos})

def pedidos(request:HttpRequest):
    return render(request, 'painel.html', context={'view': 'pedidos.html', 'title': 'Pedidos'})