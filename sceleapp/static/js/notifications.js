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
        console.log('SDSD')
        var obj_id = $(this).data('obj_id');
        console.log(obj_id)
        getNotif(obj_id)
    });

    function getNotif(obj_id){
        $.ajax({
            url: getNotifUrl,
            data: {'obj_id': obj_id},
            type: 'get',
            success: (data) => {
                console.log(data)
                var page = data['res'].page
                if (page === 'post'){
                    console.log('post')
                }
                else if (page === 'forum'){
                    window.location.replace(forum_url)
                }
            }
        });
    }
});