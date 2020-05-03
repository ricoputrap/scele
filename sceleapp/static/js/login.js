$(document).ready(function(){
    var password = $('#id_password');
    $('.show-password').click(function(){
        togglePassword()
    });

    function togglePassword() {
        var password = document.getElementById("id_password");
        if (password.type === "password") {
            password.type = "text";
        } else {
            password.type = "password";
        }
      }
});