var PEDIDO_TEMPLATE = '';

async function carregaPedidos() {
    var pedidos = await ajaxPromise('/pedidos/carregar');
    alert(pedidos);
}