/*
 * index.js holds the javascript for the index page. The javascript here
 * is used to randomly set the background image of the page
 */

// On document load specify the body background to be a random image
$(document).ready(function() {
        var r = Math.floor((Math.random() * 3) + 1);
        $("body").css("background", "url('static/img/mainbg" + r + ".png') repeat #263544");
});
