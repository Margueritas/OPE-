
  var CLASSE_CSS_SELECIONADO = 'selecionado';
  var ITEM_TEMPLATE = '';
  var CARREGANDO = '';
  var containerItens = null;

  function aplicaItens(itens) {
    var html = '';
    for(item of itens) {
      var campos = item.fields;
      html += ITEM_TEMPLATE.format(
        campos.imagem,
        campos.nome,
        campos.descricao,
        campos.preco
      );
    }
    containerItens.html(html);
  }

  function trocaTipo(tipoSelecionado) {
    $('#seletor-tipo-' + tipoAtivo).removeClass(CLASSE_CSS_SELECIONADO);
    $('#seletor-tipo-' + tipoSelecionado).addClass(CLASSE_CSS_SELECIONADO);
    tipoAtivo = tipoSelecionado;
    containerItens.html(CARREGANDO);
    $.ajax({
      url: '/cardapio/categoria?tipo=' + tipoSelecionado,
      method: 'GET'
    }).done(function(response) {
      aplicaItens(JSON.parse(response));
    });
  }