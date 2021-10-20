from django.http import JsonResponse
from django.shortcuts import render,redirect, get_list_or_404
from apps.common.models import Endereco, Usuario, ProdutoTipo, Produto, UsuarioEndereco
from apps.common.carrinho import get_carrinho_dict, save_carrinho_dict
from django.http import HttpRequest, HttpResponse
from django.core import serializers
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
    usuarios = Usuario.objects.filter(is_staff=False)
    lista_usuarios = []
    for usuario in usuarios:
        usuario_pk = UsuarioEndereco.objects.filter(idcliente=usuario.pk,primario=True).values_list('idendereco', flat=True)
        if len(usuario_pk) > 0:
            e = Endereco.objects.get(id=usuario_pk[0])
            u = {
            'pk': usuario.pk,
            'nome': usuario.nome,
            'sobrenome': usuario.sobrenome,
            'cpf': usuario.cpf,
            'telefone': usuario.telefone,
            'rua': e.logradouro,
            }
            lista_usuarios.append(u)
    return render(request, 'painel.html', context={'view': 'clientes.html', 'title': 'Clientes', 'usuarios': lista_usuarios})

def clientes_delete(request:HttpRequest, pk):
    try:
        enderecos_para_apagar = Endereco.objects.filter(id__in=UsuarioEndereco.objects.filter(idcliente=pk).all().values_list('idendereco', flat=True)).all()
        for endereco in enderecos_para_apagar:
            endereco.delete()
        Usuario.objects.get(id=pk).delete()
    except:
        print("ERRO")
    return redirect(clientes)

def clientes_pagina_editar(request, pk):
    usuario = Usuario.objects.get(id=pk)
    enderecos = UsuarioEndereco.objects.filter(idcliente=pk).all()
    enderecos_lista = []
    for endereco in enderecos:
        enderecos_lista.append({"primario": endereco.primario, "endereco": endereco.idendereco})
    retorno = {
        "usuario": usuario,
        "enderecos": enderecos_lista
    }
    return render(request, 'painel.html', context={'view': 'clientes_editar.html', 'title': 'Editar cliente', 'dados': retorno})

def clientes_cadastro(request:HttpRequest) -> HttpResponse:
    return render(request, 'painel.html', context={'view': 'clientes_cadastro.html', 'title': 'Cadastrar cliente'})

def carrinho_editar(request:HttpRequest, id_produto: int, quantidade: float, id_item: int) -> HttpResponse:
    id_produto = int(id_produto)
    quantidade = float(quantidade)
    id_item = int(id_item)
    carrinho = get_carrinho_dict(request)
    if id_item == -1:
        # item novo
        ultimo_item = -1
        for item in carrinho:
            if item['id_item'] > ultimo_item:
                ultimo_item = item['id_item']
        ultimo_item = ultimo_item + 1
        if quantidade == 1:
            item_novo = {'id_item': ultimo_item, 'produtos': []}
            item_novo['produtos'].append({'id_produto': id_produto, 'quantidade': quantidade})
            carrinho.append(item_novo)
        else:
            encontrado = False
            for item in carrinho:
                if encontrado:
                    break
                for produto in item['produtos']:
                    if produto['quantidade'] < 1 and len(item['produtos']) < 2:
                        encontrado = True
                        item['produtos'].append({'id_produto': id_produto, 'quantidade': quantidade})
                        break
            if not encontrado:
                item_novo = {'id_item': ultimo_item, 'produtos': []}
                item_novo['produtos'].append({'id_produto': id_produto, 'quantidade': quantidade})
                carrinho.append(item_novo)
    else:
        #acha item e modifica/adiciona
        item_encontrado = None
        for item in carrinho:
            if item['id_item'] == id_item:
                item_encontrado = item
                break
        if quantidade == 1 \
            or len(item_encontrado['produtos']) > 1 \
            or (len(item_encontrado['produtos']) == 1 \
            and item_encontrado['produtos'][0]['quantidade'] == 1):
            item_encontrado['produtos'] = [{'id_produto': id_produto, 'quantidade': quantidade}]
        else:
            item_encontrado['produtos'].append({'id_produto': id_produto, 'quantidade': quantidade})
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

def clientes_inserir(request:HttpRequest) -> HttpResponse:
    _ = request.POST
    try:
        endereco = Endereco.objects.create(
            logradouro = _['rua'],
            numero = _['numero'],
            bairro = _['bairro'],
            cep = _['cep'],
            complemento = _['complemento'],
            municipio = _['cidade']
        )
        novo_cliente = Usuario.objects.create(
            nome = _['nome'],
            sobrenome = _['sobrenome'],
            telefone = _['telefone'],
        )
        novo_cliente.endereco.add(endereco)
        UsuarioEndereco.objects.filter(idcliente=novo_cliente.pk, idendereco=endereco.pk).update(primario=True)
        resposta = {'status': 'sucesso'}
    except:
        resposta = {'status': Exception}
    return JsonResponse(resposta)

def clientes_editar(request:HttpRequest) -> HttpResponse:
    _ = request.POST
    try:
        Usuario.objects.filter(id=_['pk']).update(
            nome = _['nome'],
            sobrenome = _['sobrenome'],
            telefone = _['telefone'],
            )
        idendereco = UsuarioEndereco.objects.filter(idcliente=_["pk"], primario=True).values_list('idendereco', flat=True)
        if len(idendereco) > 0:
            Endereco.objects.filter(id=idendereco[0]).update(
                logradouro = _['rua'],
                numero = _['numero'],
                bairro = _['bairro'],
                cep = _['cep'],
                complemento = _['complemento'],
                municipio = _['cidade']
            )
        resposta = {"status": "sucesso"}
    except:
        resposta = {"status": "erro"}
    return JsonResponse(resposta)

def cardapio(request:HttpRequest) -> HttpResponse:
    tipos_produtos = ProdutoTipo.objects.all()
    tipo_selecionado = request.GET.get("tipo")
    tipo_ativo: ProdutoTipo
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