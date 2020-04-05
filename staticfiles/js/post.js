$(document).ready(function() {
    console.log("asass")
    $('.btn-like').on('click', function(e){
        e.preventDefault();
        console.log("clicked")
        $.ajax({
            url: 'addlike/',
            data: {'like_type':'p', 'obj_id':8},
            type: 'post',
            dataType: 'json',
            success: function (data) {
              console.log(data)
            }
          });
          return false;
    });
});