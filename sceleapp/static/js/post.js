$(document).ready(function() {
  // $('#likersModal').modal('show');
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
    // $('#likersModal').modal('show');
    var like_type = 'r';
    if ($(this).is('#postlike')) {
      like_type = 'p';
    }
    var obj_id = $(this).data('obj_id');
    if ($(this).is('.liked')){
      unlike($(this), like_type, obj_id);
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
        // $('#likersModal').modal('show');
        obj.text('Unlike');
        obj.addClass('liked')
      }
    });
  }

  function unlike(obj, like_type, obj_id) {
    $.ajax({
      url: 'unlike/',
      data: {'like_type':like_type, 'obj_id':obj_id },
      type: 'post',
      dataType: 'json',
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
      },
      success: (data) => {
        var new_quantity = data['new_quantity'];
        if (like_type === 'p'){
          var like_counter = $('#post-item .likes-count');
        }
        else {
          obj_attr = '#' + obj_id + ' .likes-count';
          var like_counter = $(obj_attr);
        }
        updateLikeCounter(like_counter, new_quantity);
        obj.text('Like');
        obj.removeClass('liked')
      }
    });
  }

  /**
   * update the like counter of a post/reply box
   * @param {*} like_counter the like counter displayed on the left-bottom corner of the box
   * @param {*} new_quantity the new quantity of likes earned on the post
   */
  function updateLikeCounter(like_counter, new_quantity) {
    if (new_quantity > 0) {
      if (new_quantity === 1) {
        like_counter.text('1 like');
      }
      else {
        like_counter.text(new_quantity + ' likes');
      }
      like_counter.removeClass('hidden');
    }
    else {
      like_counter.text('0 like');
      like_counter.addClass('hidden');
    }
  }

  $('.likes-count').click(function(e){
    e.preventDefault();
    var like_type = 'r';
    if ($(this).is('#postliker')) {
      like_type = 'p';
    }
    var obj_id = $(this).data('obj_id');
    viewLikers($(this), like_type, obj_id);
  });

  function viewLikers(obj, like_type, obj_id) {
    $.ajax({
      url: 'viewlikers/',
      data: {'like_type':like_type, 'obj_id':obj_id },
      type: 'post',
      dataType: 'json',
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
      },
      success: (data) => {
        var likers = data['response']
        var content = "";
        $.each(likers, function(key, val) {
          content += '<div class="liker-item">' + 
                        '<img src="' + pic + '" alt="user-icon">' +
                        '<p>' + val + '</p>' +
                      '</div>';
        });
        $('.modal-body').html(content);
      }
    });
  }

  $('.btn-delete').click(function(e){
    e.preventDefault();
    var obj_id = $(this).data('obj_id');
    var item_type = 'r'
    if ($(this).is('#postdelete')) {
      item_type = 'p';
    }
    openDeleteModal(obj_id, item_type)
  })

  function openDeleteModal(obj_id, item_type) {
    $('#delete-conf').modal('show')

    $('#delete').click(function(){
      delete_item(obj_id, item_type)
    });
  }

  function delete_item(obj_id, item_type){
    $.ajax({
      url: del_post_url,
      data: {'obj_id':obj_id, 'item_type': item_type},
      type: 'post',
      dataType: 'json',
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
      },
      success: (data) => {
        if (item_type === 'p') {
          window.location.replace(forum_url);
        }
        else {
          window.location.replace(post_url);
        }
      }
    });
  }
});