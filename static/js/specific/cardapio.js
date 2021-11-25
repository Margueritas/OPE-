var carrinho = {};
var itemSelecionado = '';
var clienteSelecionado = null;
var tipoAtivo = null;
var cartStatus = false;
var produtos = {};
var pedidoData = null;

var ITEM_CARRINHO_PRODUTO_TEMPLATE = '';
var ITEM_CARRINHO_TEMPLATE = '';
var VALOR_TOTAL_TEMPLATE = '';
var SELECT_CUSTOMER_TEMPLATE = '';

function iniciaCarrinho() {
    carregaCarrinho(
    $.ajax({
        url: '/carrinho/carregar',
        method: 'GET'
    })
  );
}

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

function removeProdutoDoItem(label, indexProduto) {
  var itemElement = $(label).parents('.item');
  var idItem = itemElement[0].dataset.item;
  if(itemElement.find('.item-produto').length < 2) {
    removeDoCarrinho(idItem);
    return;
  }
  carregaCarrinho(
    $.ajax({
        url: '/carrinho/editar/' + idItem + '/' + indexProduto + '/0',
        method: 'GET'
    })
  );
}

function showCarregando() {
  spinner = `<div class="spinner-border ms-2" role="status">
            <span class="visually-hidden">Loading...</span>
            </div>`
  if ($('#h2title').children('div.spinner-border').length == 0) {
    $("#h2title").append(spinner);
  }
}

function hideCarregando() {
  if ($('#h2title').children('div.spinner-border').length > 0) {
    $('#h2title').children('div.spinner-border').detach();
  }
}

async function confirmarPedido() {
  if($('#confirmar-pedido').hasClass('invalido')) {
    alert($('#confirmar-pedido').data('msg-invalido'));
    return;
  }
  console.log(pedidoData);
  for (let item of pedidoData.itens) {
    if (item.produtos.length > 1) {
      let metadeAnt = null;
      for (let metade of item.produtos) {
        if (metadeAnt == null) {metadeAnt = metade.id_tipo}
        else {if (metadeAnt != metade.id_tipo) {
          if(confirm("Sabores doce e salgado na mesma pizza. Continuar?")){
            showCarregando();
            var idPedidoNovo = await ajaxPromise('/pedidos/novo', pedidoData);
            if(isNaN(parseInt(idPedidoNovo))) {
              hideCarregando();
              alert('Ocorreu um erro ao confirmar o pedido.');
              return;
            }
            document.location.replace('/pedidos');
            }
          }
        }
      }
    }
  }
}

function carregaCarrinho(jQueryAjaxObj) {
    var mensagemValidacao = 'Pedido não pode ser concluído devido aos' +
      ' seguintes erros:\n\n';
    var valido = true;
    if(clienteSelecionado == null) {
      mensagemValidacao += '- Necessário selecionar cliente\n';
      valido = false;
      return false;
    } else {
      showCarregando();
      $('#nome').html(clienteSelecionado.nome);
      $('#sobrenome').html(clienteSelecionado.sobrenome);
      $('#rua').html(clienteSelecionado.rua);
      $('#numero').html(clienteSelecionado.numero);
      $('#telefone').html(clienteSelecionado.telefone);
      $('#virgula').html(', ');
    }
    jQueryAjaxObj.done(async function(response) {
      var item = null;
      carrinho = JSON.parse(response);
      for(item of carrinho) {
        var produtoNoItem = null;
        for(produtoNoItem of item.produtos) {
          if(produtos[produtoNoItem.id_produto] == null) {
            produtos[produtoNoItem.id_produto] = JSON.parse(await ajaxPromise('/produto?id=' + produtoNoItem.id_produto))[0];
          }
        }
      }
      var htmlTotal = '';
      var valorTotalCarrinho = 0;
      var hasItens = false;
      if(clienteSelecionado != null) {
        pedidoData = {
          cliente: clienteSelecionado.pk,
          itens: []
        };
      } else {
        pedidoData = {
          itens: []
        };
      }
      for(item of carrinho) {
        var itemData = {
          produtos: []
        }
        hasItens = true;
        var numeroItem = '' + (item.id_item + 1);
        var produtosHtml = '';
        if(numeroItem.length < 2) {
          numeroItem = '0' + numeroItem;
        }
        var precoTotal = 0;
        var produtoIndex = 0;
        var isMeio = false;
        for(produtoItem of item.produtos) {
          var produtoData = {
            id_produto: produtoItem.id_produto,
            id_tipo: '',
          };
          var produto = produtos['' + produtoItem.id_produto];
          var quantidade = '';
          if(produtoItem.quantidade < 1) {
            quantidade = '1/2';
            precoTotal += produto.fields.preco_meio;
            produtoData.preco = produto.fields.preco_meio;
            isMeio = true;
          } else {
            precoTotal += produto.fields.preco;
            produtoData.preco = produto.fields.preco;
          }
          produtoData.id_tipo = produto.fields.idtipo;
          produtoData.quantidade = produtoItem.quantidade;
          produtosHtml += ITEM_CARRINHO_PRODUTO_TEMPLATE.format(
            quantidade,
            produto.fields.nome,
            produtoIndex++
          );
          itemData.produtos.push(produtoData);
        }
        if(isMeio && produtoIndex < 2) {
          mensagemValidacao += '- Pizza '
            + (pedidoData.itens.length + 1) 
            + ' incompleta (pizza de dois sabores'
            + ' faltando segundo sabor)\n';
          valido = false;
        }
        valorTotalCarrinho += precoTotal;
        htmlTotal += ITEM_CARRINHO_TEMPLATE.format(
          numeroItem,
          produtosHtml,
          asMonetary(precoTotal),
          item.id_item
        );
        pedidoData.itens.push(itemData);
      }
      if(!hasItens) {
        htmlTotal += '<span style="margin-left: 15px;">Nenhum item no carrinho.</span>';
      }
      htmlTotal += VALOR_TOTAL_TEMPLATE.format(
        asMonetary(valorTotalCarrinho)
      );
      $('#carrinho-itens').html(htmlTotal);
      await refreshCarrinho();
      console.log("refreshCarrinho");
      if(!hasItens) {
        mensagemValidacao += '- Não existem itens no carrinho.';
        valido = false;
      }
      if(!valido) {
        $('#confirmar-pedido').addClass('invalido');
        $('#confirmar-pedido').data('msg-invalido', mensagemValidacao);
      } else {
        $('#confirmar-pedido').removeClass('invalido');
      }
      var labels = $('.label-meia').filter(function(ignored, e) {
        return e.innerHTML == '';
      });
      var label = null;
      for(label of labels) {
        $(label.parentNode.parentNode).find('.material-icons').remove();
        $(label).remove();
      }
      hideCarregando();
    });
}

function asMonetary(value) {
  var precoSplit = ('' + value).split('.');
  if(precoSplit.length < 2) {
    precoSplit.push('0');
  }
  if(precoSplit[1].length < 2) {
    precoSplit[1] = precoSplit[1] + '0';
  }
  return precoSplit.join(',');
}

async function selectCustomer(pk, iniciarCarrinho) {
  if(iniciarCarrinho) {
    $('#modalSelecionarCliente').modal('hide');
  }
  showCarregando();
  clienteSelecionado = (JSON.parse(await ajaxPromise("/clientes/" + pk + '/dados')))[0]
  hideCarregando();
  if(iniciarCarrinho) {
    iniciaCarrinho();
  }
}

function refreshCarrinho() {
  var resolve = null;
  var promise = new Promise(function(res, rej) {
    resolve = res;
  });

  $('#carrinho').css({'display': ''});
  $('#carrinho').css(
    {
      'visibility':'visible',
      'opacity':'100',
      'border':'1px solid #34675154',
      'height':$('#medida').height()+'px',
      'transition':'opacity 250ms, height 150ms ease-out'
    });
  resolve('');
  return promise
}

function toggleCarrinho() {
  var resolve = null;
  var promise = new Promise(function(res, rej) {
    resolve = res;
  });
  if($('#carrinho').css('height')==='0px'){
    $('#carrinho').css({'display': ''});
    $('#carrinho').css({'visibility':'visible','opacity':'100',
      'border':'1px solid #34675154','height':$('#medida').height()+'px',
      'transition':'opacity 250ms, height 150ms ease-out'});
      if ($('#setacarrinho').hasClass('d-none')) 
      {
        $('#setacarrinho').toggleClass('d-none');
      }
      cartStatus = true;
      resolve('');
  } else {
    $('#carrinho').css({'opacity':'0','border':'1px solid #white',
      'height':'0px','transition':'opacity 250ms, height 150ms ease-in, border-color 250ms ease'});
    setTimeout(function(){
      $('#carrinho').css({'border':'0','visibility':'collapse',
      'display': 'none'
      });
      resolve('');
    }, 270);
    if (!$('#setacarrinho').hasClass('d-none')) 
      {
        $('#setacarrinho').toggleClass('d-none');
      }
    cartStatus = false;
  }
  // $('#setacarrinho').toggleClass('d-none');
  if($('#botao-carrinho').css('background-color').toString()=='rgb(52, 103, 81)') {
    $('#botao-carrinho')
      .css('background', '#ffffff')
      .css('color', '#346751')
      .css('transition','background-color 250ms ease-in');
  } else {
    $('#botao-carrinho').css('background', '#346751').css('color', '#ffffff');
  };
  return promise
}

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
        asMonetary(campos.preco),
        item.pk,
        campos.idtipo,
        asMonetary(campos.preco_meio),
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
      } else {
        $(".btn-pizza-mei").removeClass('d-none');
        $(".btn-pizza-int").removeClass('d-none');
        $(".pizza-mei").removeClass('d-none');
        $(".btn-bebida").addClass('d-none');
      }
    });
  }
