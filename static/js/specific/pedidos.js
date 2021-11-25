var PEDIDO_TEMPLATE = '';
var PRODUTOS_TEMPLATE = '';
var CARREGANDO = '';
var containerItens = null;
var statusAtivo = null;
var CLASSE_CSS_SELECIONADO = 'selecionado';

async function carregaPedidos() {
    let pedidos = await ajaxPromise('/pedidos/carregar/1');
    return pedidos;
}

function aplicaItens(itens) {
    var html = '';

    for(item of itens) {
      let htmlProdInt = '';
      let lastProd = null;
      let total = 0;
      cliente = item.cliente[0];
      for (let produto of item.produtos) {
          total += produto.preco;
          if (produto.quantidade == 0.5) {
            if (!lastProd){
                htmlProdInt += '<div class="border rounded my-1 px-1 py-1" style="border: 1px solid #999">';
            }
            
            htmlProdInt += `
            <div class="item d-flex justify-content-between">
            <span class="item-qtd">1/2</span>
            <span class="item-descr">${produto.nome.replace('Pizza de', '')}</span>
            <span class="destaque">R$${produto.preco}</span>
            </div>`;

            if (lastProd != null) {
                if (lastProd.quantidade == 0.5) {
                    htmlProdInt += '</div>';
                    lastProd = null;
                }
            }

            lastProd = produto;
          }
          else {
              htmlProdInt += `
                <div class="item d-flex justify-content-between my-1">
                <span class="item-qtd">01</span>
                <span class="item-descr">${produto.nome.replace('Pizza de', '')}</span>
                <span class="destaque">R$${produto.preco}</span>
                </div>
              `;
              lastProd = null;
          }
      }
      html += PEDIDO_TEMPLATE.format(
        item.id,
        item.status,
        item.status_texto,
        cliente.nome,
        cliente.sobrenome,
        cliente.rua,
        cliente.numero,
        cliente.telefone,
        item.data.split("-").reverse().join("/"),
        item.hora.split('.')[0],
        htmlProdInt,
        total
      );
    }
    containerItens.html(html);
}

function trocaStatus(statusSelecionado, ordem, pesquisa) {
    $('#seletor-status-' + statusAtivo).removeClass(CLASSE_CSS_SELECIONADO);
    $('#seletor-status-' + statusSelecionado).addClass(CLASSE_CSS_SELECIONADO);
    let termoPesquisa = '';
    statusAtivo = statusSelecionado;
    containerItens.html(CARREGANDO);
    $.ajax({
      url: '/pedidos/busca?status=' + statusAtivo + '&pesquisa=' + pesquisa+ '&ordem='+ordem,
      method: 'GET'
    }).done(function(response) {
        if (ordem == undefined) $("#select-filtro-pedido").val('recentes');
      aplicaItens(JSON.parse(response));
      if (statusAtivo != 1) {
            $(".botoes-pedido").addClass('d-none');
      }
      else {
        $(".botoes-pedido").removeClass('d-none');
      }
    });
}

function finalizaPedido(idPedido) {
    $.ajax({
        url: '/pedidos/finalizar?idpedido=' + idPedido + '&status=' + statusAtivo,
        method: 'GET'
      }).done(function(response) {
        aplicaItens(JSON.parse(response));
      });
}

function cancelaPedido(idPedido) {
    $.ajax({
        url: '/pedidos/cancelar?idpedido=' + idPedido + '&status=' + statusAtivo ,
        method: 'GET'
      }).done(function(response) {
        aplicaItens(JSON.parse(response));
      });
}