$(document).ready(function() {
    // https://stackoverflow.com/questions/35112451/forbidden-csrf-token-missing-or-incorrect-django-error
    function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++){
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    function csrfSafeMethod(method){
      // these HTTP methods do not require CSRF protection
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $('.btn-like').on('click', function(e){
        e.preventDefault();
        $.ajax({
            url: 'addlike/',
            data: {'like_type':'p', 'obj_id':8},
            type: 'post',
            dataType: 'json',
            beforeSend: function(xhr, settings) {
              if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                  xhr.setRequestHeader("X-CSRFToken", csrftoken);
              }
            },
            success: function (data) {
              console.log(data)
            }
          });
          return false;
    });
});