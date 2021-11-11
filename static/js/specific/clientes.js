
function openModalDeleteUser(pk, nome, sobrenome) {
    $('#cliente-nome').html(nome);
    $('#cliente-sobrenome').html(sobrenome);
    $('#form-delete').attr('action', '/clientes/delete/' + escape(pk));
}

function editar(pk) {
    window.location.href = "/clientes/" + pk;
}

function prepareForModalIfNeeded() {
    if(isModal) {
        $('.modal-hide').css('display', 'none');
        $('.modal-show').css('display', '');
        $('#content-div').css('margin-left', '').css('width', '');
        $('#botao-add-cliente').css('visibility', 'hidden');
    }
}

function selectCustomer(pk) {
    alert(pk);
}

function novoPedido(pk) {
  window.location.href = "/cardapio/" + pk;
}

$(document).ready(function(){
	$("#botao-add-cliente").click(function() {
		window.location.href = "/clientes/cadastro";
	});

    prepareForModalIfNeeded();

  //setup before functions
  var typingTimer;                //timer identifier
  var doneTypingInterval = 500;  //time in ms, 5 second for example
  var $input = $('#pesquisacliente');

  //on keyup, start the countdown
  $input.on('keyup', function () {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(doneTyping, doneTypingInterval);
  });

  //on keydown, clear the countdown 
  $input.on('keydown', function () {
    clearTimeout(typingTimer);
  });

  //user is "finished typing," do something
  function doneTyping () {
    $.ajax({
      url: '/clientes/busca',
      method: 'GET',
      data: {"pesquisa": $input.val()}
    }).done(function(resp){
      $(".app-cards").empty();
      var string = ``;
      $(resp.clientes).each(function(index){
        var cliente = resp.clientes[index];
        string += `<div class="app-card">
        <div class="card-dados-cliente">
            <p class="item-card-dados-cliente" style="font-weight: bold;">${cliente.nome} ${cliente.sobrenome}</p>
            <p class="item-card-dados-cliente">${cliente.telefone}</p>
            <p class="item-card-dados-cliente">${cliente.rua}, ${cliente.numero}</p>
        </div>
        <div style="display: flex; justify-content: end; padding-right: 10px;">
            <button class="botao-clientes modal-hide" data-bs-toggle="modal" data-bs-target="#modalConfirmarDelete"
                onclick="openModalDeleteUser('${cliente.pk}', '${cliente.nome}', '${cliente.sobrenome}', '${cliente.telefone}');">
                <span class="material-icons">delete_outline</span>
                <span class="label-botao-clientes">excluir</span>
            </button>
            <button class="botao-clientes modal-hide" onclick="editar('${cliente.pk}')">
                <span class="material-icons">edit</span>
                <span class="label-botao-clientes">editar</span>
            </button>
            <button class="botao-clientes modal-hide" onclick="novoPedido('${cliente.pk}')">
                <span class="material-icons">menu_book</span>
                <span class="label-botao-clientes">novo pedido</span>
            </button>
            <button class="botao-clientes modal-show" style="display: none;" onclick="top.selectCustomer('${cliente.pk}', true)">
                <span class="material-icons">done</span>
                <span class="label-botao-clientes">selecionar</span>
            </button>
        </div>
    </div>`;
  });
    $(".app-cards").append(string);
    prepareForModalIfNeeded();
    });
  }
});