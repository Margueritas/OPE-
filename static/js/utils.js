if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) { 
            return typeof args[number] != 'undefined'
                ? args[number]
                : match
            ;
        });
    };
}

function ajaxPromise(url, body) {
    var method = 'POST';
    var data = null;
    if(body == undefined) {
      method = 'GET';
    } else {
      var formData = new FormData();
      data = JSON.stringify(body);
      // formData.append('data', body);
    }
    var resolve = null;
    var reject = null;
    var promise = new Promise(function(res, rej) {
      resolve = res;
      reject = rej;
    });
    $.ajax({
      url: url,
      type: method,
      data: data,
      csrfmiddlewaretoken: window.CSRF_TOKEN,
      processData: false,
      mimeType: "multipart/form-data",
      contentType: false,
      cache: false,
    }).done(function(response) {
      resolve(response);
    }).fail(function(ig1, ig2, error) {
      reject(error)
    });
    return promise;
  }
  