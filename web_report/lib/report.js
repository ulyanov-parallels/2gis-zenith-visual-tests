$(document).ready(function(){
    $('[data-fancybox="gallery"]').fancybox({
        animationEffect: false,
        transitionEffect: false,
        buttons: [
            "zoom",
            "slideShow",
            "fullScreen",
            "close",
        ],
        fullScreen : {
            autoStart : true,
        },
        iframe : {
            preload : false,
        },
        slideShow : {
            autoStart : false,
            speed     : 1000
        },
    });
});

jQuery.fn.toggleText = function() {
    var altText = this.data("alt-text");

    if (altText) {
        this.data("alt-text", this.html());
        this.html(altText);
    }
};

$(document).ready(function(){
    $('[data-toggle="offcanvas"]').click(function ()  {
        $(this).toggleText();
    });
});

$(document).ready(function() {
    $(".collapse").trigger('click');
});