function resize() {
    var contentheight = Math.floor($(window).height());
    console.log(contentheight);
    var tableheight = contentheight - 230;
    console.log(tableheight);
    $('#id_table_container').css('max-height', tableheight + 'px');
}

$(document).ready(function(){
    resize();
    window.onresize = function() {
        resize();
    };
});

