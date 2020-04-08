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
      if ($(this).is('.liked')){
        console.log('has liked');
      }
      else {
        addlike($(this), like_type, obj_id);
      }
      
    });

    /**
     * Add a like on a post/reply
     * @param {*} obj the html element that was clicked: anchor tag on 'Like"
     * @param {*} like_type the type of the element that was liked: p (post) or r (reply)
     * @param {*} obj_id the ID of a like anchor & the box item
     */
    function addlike(obj, like_type, obj_id){
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
          var new_quantity = data['likes'].quantity;
          if (like_type === 'p'){
            var like_counter = $('#post-item .likes-count');
          }
          else {
            obj_attr = '#' + obj_id + ' .likes-count';
            var like_counter = $(obj_attr);
          }
          updateLikeCounter(like_counter, new_quantity);
          obj.text('Unlike');
          obj.addClass('liked')
        }
      });
    }

    function unlike(obj, like_type, obj_id) {
      
    }

    /**
     * update the like counter of a post/reply box
     * @param {*} like_counter the like counter displayed on the left-bottom corner of the box
     * @param {*} new_quantity the new quantity of likes earned on the post
     */
    function updateLikeCounter(like_counter, new_quantity) {
      if (new_quantity > 1) {
        like_counter.text(new_quantity + ' likes');
      }
      else {
        like_counter.text('1 like');
      }
      like_counter.removeClass('hidden');
    }
});