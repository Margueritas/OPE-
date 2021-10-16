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