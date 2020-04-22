$(document).ready(function(){
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

    $('.notif-item').click(function(e){
        var obj_id = $(this).data('obj_id');
        console.log(obj_id)
        openAndUpdateNotifItem(obj_id)

        // remove "baru" label/badge
        var selector = '#' + obj_id + ' .badge'
        $(selector).remove()
    });

    function openAndUpdateNotifItem(obj_id){
        var postUrl = post_url.substr(0,12)
        $.ajax({
            url: notif_url,
            data: {'obj_id': obj_id},
            type: 'post',
            dataType: 'json',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: (data) => {
                var res = data['res']
                console.log(res)
                if ('page' in res) {
                    var page = res.page;
                }
                
                if ('is_badge' in res){
                    content =   '<div class="modal-content__content-area">' +
                                    '<img src="' + res.img_loc + '" alt="badge-img">' +
                                    '<h3>Selamat!</h3>' +
                                    '<p>' + res.desc + '</p>' +
                                    '<button type="close" class="btn btn--block btn--green" data-dismiss="modal">OK</button>' +
                                '</div>'
                    if (page === 'post') {
                        postUrl = postUrl + data['res'].id
                        content += '<hr><a href="' + postUrl + '" class="font-bold">Lihat ' + page + '</a>'
                    }
                    else if (page === 'reply') {
                        var replyUrl = postUrl + data['res'].post_id + '#' + data['res'].id
                        content += '<hr><a href="' + replyUrl + '" class="font-bold">Lihat ' + page + '</a>'
                    }
                    $('.modal-body').html(content);
                    $('#modal').modal('show');
                }
                else {
                    if (page === 'post'){
                        postUrl = postUrl + data['res'].id
                        window.location.replace(postUrl)
                    }
                    else if (page === 'forum'){
                        window.location.replace(forum_url)
                    }
                    else if (page === 'reply'){
                        var replyUrl = postUrl + data['res'].post_id + '#' + data['res'].id
                        window.location.replace(replyUrl)
                    }
                }
            }
        });
    }
});