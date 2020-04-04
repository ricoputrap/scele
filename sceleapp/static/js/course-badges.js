$(document).ready(function(){
    $('#badge-skill').on('click', function(e){
        $('.participatory-badge').addClass("collapse");
        $('.skill-badge').removeClass("collapse");
    });
    $('#badge-participation').on('click', function(e){
        $('.skill-badge').addClass("collapse");
        $('.participatory-badge').removeClass("collapse");
    });
});