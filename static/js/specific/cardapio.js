var carrinho = {};
var itemSelecionado = '';
var clienteSelecionado = null;
var tipoAtivo = null;

function adicionaNoCarrinho(idProduto, quantidade) {
  carregaCarrinho(
    $.ajax({
        url: '/carrinho/editar/-1/' + idProduto + '/' + quantidade,
        method: 'GET'
    })
  );
}

function removeDoCarrinho(idItem) {
  carregaCarrinho(
    $.ajax({
        url: '/carrinho/deletar/' + idItem,
        method: 'GET'
    })
  );
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

function selectCustomer(pk) {
  clienteSelecionado = pk;
  alert('cliente selecionado é o ' + pk);
}

function toggleCarrinho() {
  
  if($('#carrinho').css('height')==='0px'){
    $('#carrinho').css({'visibility':'visible','opacity':'100','border':'1px solid #34675154','height':$('#medida').height()+'px','transition':'opacity 250ms, height 150ms ease-out'});
  }
  else {
    $('#carrinho').css({'opacity':'0','border':'1px solid #white','height':'0','transition':'opacity 250ms, height 150ms ease-in, border-color 250ms ease'});
    setTimeout(function(){
      $('#carrinho').css({'border':'0','visibility':'collapse'});
    }, 270);
  };
  $('#setacarrinho').toggleClass('d-none');
  if($('#botao-carrinho').css('background-color').toString()=='rgb(52, 103, 81)') {
    $('#botao-carrinho').css('background', '#ffffff').css('color', '#346751').css('transition','background-color 250ms ease-in');
  }
  else {
    $('#botao-carrinho').css('background', '#346751').css('color', '#ffffff');
  };
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
    if(termoPesquisa.length == 0 || termoPesquisa.length >= 2) {
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
        item.pk,
        campos.idtipo,
        campos.preco_meio,
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
      url: '/cardapio/busca?tipo=' + tipoSelecionado + '&pesquisa=' + termoPesquisa,
      method: 'GET'
    }).done(function(response) {
      aplicaItens(JSON.parse(response));

      if(JSON.parse(response)[1].fields.idtipo === 3) {
        $(".btn-pizza-mei").addClass('d-none');
        $(".btn-pizza-int").addClass('d-none');
        $(".pizza-mei").addClass('d-none');
        $(".btn-bebida").removeClass('d-none');
      }
      else{
        $(".btn-pizza-mei").removeClass('d-none');
        $(".btn-pizza-int").removeClass('d-none');
        $(".pizza-mei").removeClass('d-none');
        $(".btn-bebida").addClass('d-none');
      }
    });
  }
