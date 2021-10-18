from django.http import JsonResponse
from django.shortcuts import render,redirect
from apps.common.models import Endereco, Usuario, ProdutoTipo, Produto, UsuarioEndereco

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('painel')
    else:
        return redirect('login')

def painel(request):
    return render(request, 'painel.html', context={'view': 'pedidos.html', 'title': 'Pedidos'})

def clientes(request):
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

def clientes_delete(request, pk):
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

def clientes_cadastro(request):
    return render(request, 'painel.html', context={'view': 'clientes_cadastro.html', 'title': 'Cadastrar cliente'})

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
        UsuarioEndereco.objects.filter(idcliente=novo_cliente.pk, idendereco=endereco.pk).update(primario=True)
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