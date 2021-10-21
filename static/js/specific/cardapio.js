var carrinho = {};
var itemSelecionado = '';

function abreModalQuantidade(idItem, nomeItem) {
    itemSelecionado = idItem;
    $('#nome-produto-quantidade').html(nomeItem);
}

function alteraNoCarrinho(idItem, quantidade) {
    if(quantidade < 0.01) {
        carregaCarrinho(
            $.ajax({
                url: '/carrinho/deletar/' + idItem,
                method: 'GET'
            })
        );
    } else {
        carregaCarrinho(
            $.ajax({
                url: '/carrinho/editar/' + idItem + '/' + quantidade,
                method: 'GET'
            })
        );
    }
}

function carregaCarrinho(jQueryAjaxObj) {
    jQueryAjaxObj.done(function(response) {
        carrinho = JSON.parse(response);
        alert('protótipo: seu carrinho consiste de (JSON) -> '+ JSON.stringify(carrinho));
    });
}

$(document).ready(function() {
    carregaCarrinho(
        $.ajax({
            url: '/carrinho/carregar',
            method: 'GET'
        })
    );
});



  var CLASSE_CSS_SELECIONADO = 'selecionado';
  var ITEM_TEMPLATE = '';
  var CARREGANDO = '';
  var containerItens = null;
  var CAMPO_PESQUISA_PIZZA = null;
  var BOTAO_PESQUISA_PIZZA = null;
  var termoPesquisa = '';
  var oldTermoPesquisa = '';

  
$(document).ready(function() {

  CAMPO_PESQUISA_PIZZA = $('#pizza-busca');
  BOTAO_PESQUISA_PIZZA = $('#pizza-busca-execute');
  var funPesquisa = function() {
    termoPesquisa = CAMPO_PESQUISA_PIZZA.val();
    if(oldTermoPesquisa != termoPesquisa) {
      oldTermoPesquisa = termoPesquisa;
    } else {
      return;
    }
    if(termoPesquisa.length == 0 || termoPesquisa.length >= 3) {
      trocaTipo(tipoAtivo);
    }
  };

  CAMPO_PESQUISA_PIZZA.on('keyup', funPesquisa);
  BOTAO_PESQUISA_PIZZA.on('click', funPesquisa);
});

  function aplicaItens(itens) {
    var html = '';
    for(item of itens) {
      var campos = item.fields;
      html += ITEM_TEMPLATE.format(
        campos.imagem,
        campos.nome,
        campos.descricao,
        campos.preco,
        campos.id,
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
      url: '/cardapio/categoria?tipo=' + tipoSelecionado + '&pesquisa=' + termoPesquisa,
      method: 'GET'
    }).done(function(response) {
      aplicaItens(JSON.parse(response));
    });
  }
