function resize() {
    if (frame_height !== undefined) {
        var contentheight = Math.floor($(window).height());
        var tableheight = contentheight - frame_height;
        $('.table-responsive-sm').css('height', tableheight + 'px');
        return tableheight;
    } 
}

$(document).ready(function(){
    tableHeight = resize();
    window.onresize = function() {
        tableHeight = resize();
    };
});

