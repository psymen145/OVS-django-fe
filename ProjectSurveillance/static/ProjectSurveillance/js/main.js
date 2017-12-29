$(document).ready(function () {
    //cache
    let $analysis = $("#analysis"),
        $fa_caret_down = $(".fa-caret-down");
    
    if($(window).width() < 576){
        $("#sidebar-toggle").prop("checked", true);
    }  

    let resizeTimeout;
    $(window).resize(function() {
        if(!!resizeTimeout){ clearTimeout(resizeTimeout); }
        resizeTimeout = setTimeout(function(){
            let win = $(this);
            if (win.width() < 576) {
                $("#sidebar-toggle").prop("checked", true);
            }
        },500);
    });

    $(document).on("click", ".clickable-row", function () {
        location.href = $(this).data('href');
    });

    $analysis.on("click", function () {
        $fa_caret_down.toggleClass("down");
    });
});