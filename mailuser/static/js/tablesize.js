function resize() {
    if (frame_height !== 'undefined') {
        var contentheight = Math.floor($(window).height());
        var tableheight = contentheight - frame_height;
        $('.table-responsive-sm').css('height', tableheight + 'px');
    } 
}

$(document).ready(function(){
    resize();
    window.onresize = function() {
        resize();
    };
});

