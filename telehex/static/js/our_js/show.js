/*
 * show.js is the JavaScript for various aspects of the show page, including
 * generating the rating bars and providing the tooltips for the episode description
 */
 
/*
 * Waits for the page to load before adding tablesorter, episode tooltips, etc.
 */
$(document).ready(function () {

    // Get the location hash from the url. If it exists then collapse the first panel
    // and expand the panel the location hash resides within
    if (location.hash) {
        $(location.hash).closest('.panel-collapse').removeClass("collapse").addClass("in");
        $(location.hash).css('background-color', '#2986b9');
        $(location.hash).animate({
            'background-color': "transparent"
        }, 4000);
    } else {
        $('#accordion').find('.panel-collapse').first().removeClass("collapse").addClass("in");
    }

    // For each column in the table find the width of the rating bar and add a width attribute
    // to the rating -0bar div
    $(".rating-col").each(function () {
        var r = $(this).children('.rating-num').text();
        $(this).children('.rating-bar').css('width', (r * 10) + "%");
    });

    $('.seasontable').tablesorter({
        // Sort the first column in ascending order, by default: sortList: [[0,0]] 
        // Make jQuery TableSort use the data-sort-value attribute, if available
        // Otherwise, just fall back to the text in the table cell. Mainly 
        // Used for sorting dates
        textExtraction: function (node) {
            var attr = $(node).attr('data-sort-value');
            if (typeof attr !== 'undefined' && attr !== false) {
                return attr;
            }
            return $(node).text();
        }
    });

    // Add a balloon tooltip for any episodes that have descriptions
    $('.balloon').each(function () {
        $(this).balloon({
            contents: $(this).children(".ep-desc").html(),
            tipSize: 5,
            delay: 200,
            position: "bottom right",
            // Add the css to the balloon tooltip
            css: {
                backgroundColor: '#292929',
                border: 'solid 2px #292929',
                'box-shadow': 'none',
                color: 'white',
                'font-size': '0.9em',
                opacity: '1',
                padding: '10px',
                width: '400px'
            },
            hideDuration: 600
        });
    });
});