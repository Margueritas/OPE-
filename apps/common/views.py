import datetime
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from apps.common.models import Endereco, Produto, Usuario,\
    ProdutoTipo, UsuarioEndereco,\
    Pedido, ProdutoPedido, StatusPedido, FormaPagamento
from apps.common.business.rules.carrinho import clear_carrinho_dict,\
    get_carrinho_dict, save_carrinho_dict
from apps.common.business.rules.clientes import load_cliente_data
from apps.common.business.rules.produtos import buscar_produtos
from django.http import HttpRequest, HttpResponse
from django.core import serializers
from datetime import datetime
import json

# Create your views here.
def index(request:HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('painel')
    else:
        return redirect('login')

def painel(request:HttpRequest) -> HttpResponse:
    return redirect('clientes')
    # return render(request, 'painel.html', \
    #     context={'view': 'clientes.html', 'title': 'Clientes', \
    #         'auxiliar': 'blank.html', 'sidebar': 'sidebar.html'})

def clientes_modal(request:HttpRequest) -> HttpResponse:
    lista_usuarios = load_cliente_data(None, None)
    return render(request, 'painel.html', \
        context={'view': 'clientes.html', 'title': 'Selecione um cliente', \
            'usuarios': lista_usuarios, 'auxiliar': 'blank.html', \
                'sidebar': 'blank.html', 'is_modal': '1'})

def clientes(request:HttpRequest) -> HttpResponse:
    lista_usuarios = load_cliente_data(None, None)
    return render(request, 'painel.html', \
        context={'view': 'clientes.html', 'title': 'Clientes', \
            'usuarios': lista_usuarios, 'auxiliar': 'blank.html', \
                'sidebar': 'sidebar.html', 'is_modal': '0'})

def clientes_busca(request:HttpRequest) -> HttpResponse:
    pesquisa = request.GET['pesquisa']
    resposta_clientes = load_cliente_data(None, pesquisa)
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

def clientes_pagina_editar(request:HttpRequest, pk) -> HttpResponse:
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
        'title': 'Editar cliente', 'dados': retorno, 'auxiliar': 'blank.html', \
            'sidebar': 'sidebar.html'})

def clientes_dados(request:HttpRequest, pk) -> HttpResponse:
    aux = Usuario.objects.get(id=pk)
    cliente = load_cliente_data(aux, None)
    return HttpResponse(json.dumps(cliente))

def clientes_cadastro(request:HttpRequest) -> HttpResponse:
    return render(request, 'painel.html', context={'view': 'clientes_cadastro.html', \
        'title': 'Cadastrar cliente', 'auxiliar': 'blank.html', \
            'sidebar': 'sidebar.html'})

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
        #acha item e modifica/adiciona/remove
        item_encontrado = None
        for item in carrinho:
            if item['id_item'] == id_item:
                item_encontrado = item
                break
        if quantidade == 0:
            del item_encontrado['produtos'][id_produto]
        elif quantidade == 1 \
            or len(item_encontrado['produtos']) > 1 \
            or (len(item_encontrado['produtos']) == 1 \
            and item_encontrado['produtos'][0]['quantidade'] == 1):
            item_encontrado['produtos'] = [{'id_produto': id_produto, 'quantidade': quantidade}]
        else:
            item_encontrado['produtos'].append({'id_produto': id_produto, 'quantidade': quantidade})
    resp = HttpResponse(json.dumps(carrinho))
    save_carrinho_dict(resp, carrinho)
    return resp

def carrinho_deletar(request:HttpRequest, id:int) -> HttpResponse:
    id = int(id)
    carrinho = get_carrinho_dict(request)
    posicao = None
    i = 0
    for item in carrinho:
        if item['id_item'] == id:
            posicao = i
            break
        else:
            i = i + 1
    del carrinho[posicao]
    resp = HttpResponse(json.dumps(carrinho))
    save_carrinho_dict(resp, carrinho)
    return resp

def carrinho_carregar(request:HttpRequest) -> HttpResponse:
    return HttpResponse(json.dumps(get_carrinho_dict(request)))

def clientes_inserir(request:HttpRequest) -> HttpResponse:
    _ = request.POST
    busca_duplicado = Usuario.objects.filter(telefone=_['telefone'])
    if len(busca_duplicado) > 0:
        return JsonResponse({'status':'duplicado'})
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

def clientes_editar(request:HttpRequest) -> HttpResponse:
    _ = request.POST
    busca_duplicado = Usuario.objects.filter(telefone=_['telefone']).exclude(id=_['pk'])
    if len(busca_duplicado) > 0:
        return JsonResponse({'status':'duplicado'})
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
    return cardapio_cliente(request, '')

def cardapio_cliente(request:HttpRequest, cliente_selecionado: str) -> HttpResponse:
    tipos_produtos = ProdutoTipo.objects.all()
    tipo_selecionado = request.GET.get("tipo")
    tipo_ativo: ProdutoTipo
    if not tipo_selecionado:
        tipo_ativo = ProdutoTipo.objects.get(tipo="Pizzas Salgadas")
    else:
        tipo_ativo = ProdutoTipo.objects.get(id=tipo_selecionado)
    return render(request, 'painel.html', context={'view': 'cardapio.html', \
        'title': 'Cardápio', 'tipos': tipos_produtos, \
            "tipo_ativo": tipo_ativo, 'auxiliar': 'cardapio_busca.html', \
                'sidebar': 'sidebar.html', 'cliente_selecionado': cliente_selecionado})

def cardapio_busca(request:HttpRequest) -> HttpResponse:
    tipo_desejado = request.GET.get("tipo")
    pesquisa = request.GET.get('pesquisa')
    produtos_buscados = buscar_produtos(tipo_desejado, pesquisa, -1)
    return HttpResponse(serializers.serialize('json', produtos_buscados, fields=('nome', 'descricao', 'preco', 'imagem', 'idtipo', 'preco_meio')))

def buscar_produto(request:HttpRequest) -> HttpResponse:
    id = request.GET.get("id")
    produtos_buscados = buscar_produtos(None, None, int(id))
    return HttpResponse(serializers.serialize('json', produtos_buscados, fields=('nome', 'descricao', 'preco', 'imagem', 'idtipo', 'preco_meio')))

@csrf_exempt
def pedidos_novo(request:HttpRequest) -> HttpResponse:
    _ = json.loads(request.body)
    id_cliente = _['cliente']
    status_preparacao = "Em preparação"
    forma_pagamento = "Crédito"
    obs=_['observacoes']
    pedido = Pedido.objects.create(obs=obs, data=datetime.now(),\
            hora=datetime.now(),\
            idstatus = StatusPedido.objects.filter(status=status_preparacao).get(),\
            idformapagamento = FormaPagamento.objects.filter(forma=forma_pagamento).get(),\
            idcliente = Usuario.objects.get(id=id_cliente))
    id_pedido = pedido.pk
    index = 1
    for item in _['itens']:
        for produto_item in item['produtos']:
            ProdutoPedido.objects.create(quantidade = produto_item['quantidade'],\
                preco = produto_item['preco'], idpedido = pedido,\
                    idproduto = Produto.objects.filter(pk=produto_item['id_produto']).get(),\
                    id = (id_pedido * 100) + index)
            index = index + 1
    response = HttpResponse(id_pedido)
    clear_carrinho_dict(response)
    return response

def pedidos_carregar(request:HttpRequest, pk:int) -> HttpResponse:
    # status_preparacao = StatusPedido.objects.get(pk=pk)
    pedidos = Pedido.objects.filter(Q(idstatus = StatusPedido.objects.filter(id=pk).get())).all()
    pedidos_tela = []
    for pedido in pedidos:
        cliente = load_cliente_data(pedido.idcliente, None)
        pedido_atual = {
            'cliente': cliente,
            'id': pedido.pk,
            'status': pedido.idstatus.pk,
            'status_texto': pedido.idstatus.status,
            'data': pedido.data.isoformat(),
            'hora': pedido.hora.isoformat(),
            'obs': pedido.obs
        }
        pedido_atual['produtos'] = []
        pedido_produtos = ProdutoPedido.objects.filter(idpedido=pedido.pk).all()
        for pedido_produto in pedido_produtos:
            produto = Produto.objects.filter(pk=pedido_produto.idproduto.pk).get()
            produto_lista = {
                'nome': produto.nome,
                'preco': pedido_produto.preco,
                'quantidade': pedido_produto.quantidade
            }
            pedido_atual['produtos'].append(produto_lista)
        pedidos_tela.append(pedido_atual)
    return HttpResponse(json.dumps(pedidos_tela))

def pedidos_busca(request:HttpRequest) -> HttpResponse:
    status_selecionado = request.GET.get("status")
    pesquisa = request.GET.get("pesquisa")
    ordenacao = request.GET.get("ordem")
    pedidos = Pedido.objects.filter(Q(idstatus = StatusPedido.objects.filter(id=status_selecionado).get())).all()
    if pesquisa and pesquisa != 'undefined':
        pedidos = pedidos.filter(Q(idcliente__nome__icontains=pesquisa) | Q(idcliente__sobrenome__icontains=pesquisa))
    if ordenacao is not None:
        if ordenacao == 'recentes' or ordenacao == 'undefined':
            pedidos = pedidos.order_by('-data', '-hora')
        elif ordenacao == 'antigos':
            pedidos = pedidos.order_by('data', 'hora')
    pedidos_tela = []
    for pedido in pedidos:
        cliente = load_cliente_data(pedido.idcliente, None)
        pedido_atual = {
            'cliente': cliente,
            'id': pedido.pk,
            'status': pedido.idstatus.pk,
            'status_texto': pedido.idstatus.status,
            'data': pedido.data.isoformat(),
            'hora': pedido.hora.isoformat(),
            'obs': pedido.obs
        }
        pedido_atual['produtos'] = []
        pedido_produtos = ProdutoPedido.objects.filter(idpedido=pedido.pk).all()
        for pedido_produto in pedido_produtos:
            produto = Produto.objects.filter(pk=pedido_produto.idproduto.pk).get()
            produto_lista = {
                'nome': produto.nome,
                'preco': pedido_produto.preco,
                'quantidade': pedido_produto.quantidade
            }
            pedido_atual['produtos'].append(produto_lista)
        pedidos_tela.append(pedido_atual)
    return HttpResponse(json.dumps(pedidos_tela))

def pedidos_finalizar(request:HttpRequest) -> HttpResponse:
    status_pagina = request.GET.get("status")
    pk = request.GET.get("idpedido")
    status_preparacao = "Finalizado"
    Pedido.objects.filter(pk=pk).update(
        idstatus = StatusPedido.objects.filter(status=status_preparacao).get()
    )
    return pedidos_carregar(request, status_pagina)

def pedidos_cancelar(request:HttpRequest) -> HttpResponse:
    status_pagina = request.GET.get("status")
    pk = request.GET.get("idpedido")
    status_preparacao = "Cancelado"
    Pedido.objects.filter(pk=pk).update(
        idstatus = StatusPedido.objects.filter(status=status_preparacao).get()
    )
    return pedidos_carregar(request, status_pagina)

def pedidos(request:HttpRequest) -> HttpResponse:
    statusPedidos = StatusPedido.objects.all()
    status_selecionado = request.GET.get("status")
    status_ativo: StatusPedido
    if not status_selecionado:
        status_ativo = StatusPedido.objects.get(status="Em preparação")
    else:
        status_ativo = StatusPedido.objects.get(id=status_selecionado)
    return render(request, 'painel.html', context={\
        'view': 'pedidos.html', 'title': 'Pedidos', 'auxiliar': 'blank.html',\
        'sidebar': 'sidebar.html', 'statusPedidos': statusPedidos,\
        'statusAtivo': status_ativo})