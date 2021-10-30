from apps.common.models import Endereco, Usuario, UsuarioEndereco
from django.db.models import Q

def load_cliente_data(pesquisa: str) -> list:
    if pesquisa == '' or pesquisa is None:
        usuarios = Usuario.objects.filter(is_staff=False)
    else:
        usuarios = Usuario.objects.filter(Q(nome__icontains=pesquisa) \
            | Q(sobrenome__icontains=pesquisa) | \
                Q(telefone__icontains=pesquisa) & Q(is_staff=False))
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
    return lista_usuarios