
from apps.common.models import ProdutoTipo, Produto

def buscar_produtos(tipo_desejado: int, pesquisa: str, id: int):
    if pesquisa is None:
        pesquisa = ''
    if id != -1:
        produtos_buscados = Produto.objects.filter(pk=id, nome__icontains=pesquisa)
    else:
        tipo = ProdutoTipo.objects.get(id=tipo_desejado)
        produtos_buscados = Produto.objects.filter(idtipo=tipo, nome__icontains=pesquisa)
    return produtos_buscados