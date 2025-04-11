$(document).ready(function() {
    $(window).scroll(function() {
        if ($(this).scrollTop()>50){
            $('#headerNav').addClass('navbar-scrolled');
        } else {
            $('#headerNav').removeClass('navbar-scrolled');
        }
    })
})
