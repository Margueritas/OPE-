from django.db.models import Q
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
    return render(request, 'painel.html', \
        context={'view': 'pedidos.html', 'title': 'Pedidos', 'auxiliar': 'blank.html'})

def clientes(request:HttpRequest) -> HttpResponse:
    usuarios = Usuario.objects.filter(is_staff=False)
    lista_usuarios = []
    for usuario in usuarios:
        usuario_pk = UsuarioEndereco.objects.filter(idcliente=usuario.pk,primario=True).values_list('idendereco', flat=True)
        if len(usuario_pk) > 0:
            tel = usuario.telefone
            e = Endereco.objects.get(id=usuario_pk[0])
            u = {
            'pk': usuario.pk,
            'nome': usuario.nome,
            'sobrenome': usuario.sobrenome,
            'cpf': usuario.cpf,
            'telefone': f'({tel[0:2]}) {tel[2:7]}-{tel[7:]}',
            'rua': e.logradouro,
            'numero': e.numero,
            }
            lista_usuarios.append(u)
    return render(request, 'painel.html', \
        context={'view': 'clientes.html', 'title': 'Clientes', \
            'usuarios': lista_usuarios, 'auxiliar': 'blank.html'})

def clientes_busca(request):
    pesquisa = request.GET['pesquisa']
    if pesquisa == '':
        clientes_filtrados = Usuario.objects.filter(is_staff=False)
    else:
        clientes_filtrados = Usuario.objects.filter(Q(nome__icontains=pesquisa) | Q(sobrenome__icontains=pesquisa) | Q(telefone__icontains=pesquisa) & Q(is_staff=False))
    resposta_clientes = []
    for cliente in clientes_filtrados:
        endereco_cliente_pk = UsuarioEndereco.objects.filter(idcliente=cliente.pk,primario=True).values_list('idendereco', flat=True)
        if len(endereco_cliente_pk) > 0:
            tel = cliente.telefone
            endereco = Endereco.objects.get(id=endereco_cliente_pk[0])
            obj_cliente = {
            'pk': cliente.pk,
            'nome': cliente.nome,
            'sobrenome': cliente.sobrenome,
            'telefone': f'({tel[0:2]}) {tel[2:7]}-{tel[7:]}',
            'rua': endereco.logradouro,
            'numero': endereco.numero,
            }
            resposta_clientes.append(obj_cliente)
    return JsonResponse({"clientes": resposta_clientes}, safe=False)

def clientes_delete(request:HttpRequest, pk):
    try:
        enderecos_para_apagar = Endereco.objects.filter( \
            id__in=UsuarioEndereco.objects.filter(idcliente=pk).all().values_list('idendereco', flat=True)).all()
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
    return render(request, 'painel.html', context={'view': 'clientes_editar.html', \
        'title': 'Editar cliente', 'dados': retorno, 'auxiliar': 'blank.html'})

def clientes_cadastro(request:HttpRequest) -> HttpResponse:
    return render(request, 'painel.html', context={'view': 'clientes_cadastro.html', \
        'title': 'Cadastrar cliente', 'auxiliar': 'blank.html'})

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

def clientes_inserir(request):
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
        UsuarioEndereco.objects.filter(idcliente=novo_cliente.pk, \
            idendereco=endereco.pk).update(primario=True)
        resposta = {'status': 'sucesso'}
    except:
        resposta = {'status': Exception}
    return JsonResponse(resposta)

def clientes_editar(request):
    _ = request.POST
    try:
        Usuario.objects.filter(id=_['pk']).update(
            nome = _['nome'],
            sobrenome = _['sobrenome'],
            telefone = _['telefone'],
            )
        idendereco = UsuarioEndereco.objects.filter( \
            idcliente=_["pk"], primario=True).values_list('idendereco', flat=True)
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
    return render(request, 'painel.html', context={'view': 'cardapio.html', \
        'title': 'Cardápio', 'tipos': tipos_produtos, \
            "tipo_ativo": tipo_ativo, 'auxiliar': 'cardapio_busca.html'})

def cardapio_busca(request:HttpRequest) -> HttpResponse:
    tipo_desejado = request.GET.get("tipo")
    pesquisa = request.GET.get('pesquisa')
    if pesquisa is None:
        pesquisa = ''
    tipo = ProdutoTipo.objects.get(id=tipo_desejado)
    produtos_buscados = Produto.objects.filter(idtipo=tipo, nome__icontains=pesquisa)
    return HttpResponse(serializers.serialize('json', produtos_buscados, fields=('nome', 'descricao', 'preco', 'imagem', 'idtipo')))

def pedidos(request:HttpRequest) -> HttpResponse:
    return render(request, 'painel.html', context={ \
        'view': 'pedidos.html', 'title': 'Pedidos', 'auxiliar': 'blank.html'})