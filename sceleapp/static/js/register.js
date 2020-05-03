$(document).ready(function(){
    $('#show-password1').click(function(){
        togglePassword("id_password1")
    });

    $('#show-password2').click(function(){
        togglePassword("id_password2")
    })

    function togglePassword(obj_id) {
        var password = document.getElementById(obj_id);
        if (password.type === "password") {
            password.type = "text";
        } else {
            password.type = "password";
        }
    }
});