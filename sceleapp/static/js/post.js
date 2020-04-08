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
    $('.btn-like').click(function(e) {
      e.preventDefault();
      var like_type = 'r';
      if ($(this).is('#postlike')) {
        like_type = 'p';
      }
      var obj_id = $(this).data('obj_id');
      console.log(obj_id)
      
      $.ajax({
          url: 'addlike/',
          data: {'like_type':like_type, 'obj_id':obj_id },
          type: 'post',
          dataType: 'json',
          beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
          },
          success: (data) => {
            console.log(data);
            var new_quantity = data['likes'].quantity;
            if (new_quantity > 1) {
              $('.likes-count').text(new_quantity + ' likes');
            }
            else {
              $('.likes-count').text('1 like');
            }
            console.log('type: ' + like_type);
            if (like_type === 'p'){
              if (new_quantity > 1) {
                $('#post-item .likes-count').text(new_quantity + ' likes');
              }
              else {
                $('#post-item .likes-count').text('1 like');
              }
            }
            else {
              
            }
            $('.likes-count').removeClass('hidden');
            $(this).text('Unlike');
            $(this).addClass('liked')
          }
        });
        return false;
    });
});