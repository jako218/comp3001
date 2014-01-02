/*
 * utils.js is a file for the javascript used on all of our pages that can't otherwise be organised.
 * isValidSearch returns a boolean depending on if the search at the given search_input_id is valid or not
 * show_loading_overlay displays the loading gif for when the page is changing
 * $document.ready() contains two annonymous functions for after the page has loaded:
 * 1. The first is a function to display the loading gif when a link is clicked
 * 2. Prepares the autocomplete function for searching.
 */


/*
 * isValidSearch takes the id of the text input for the search form and returns a boolean whether the form is valid or not.
 * If the form is valid, the loading overlay is shown and true is returned.
 * If the form is not valid, false is returned, the placeholder text changes and in the case of the big search, the input box rumbles.
 */
function isValidSearch(search_input_id) {
        var input = $('#' + search_input_id);
        var form = $('.form-group');
        form.jrumble({ speed: 30 }); // Initialise jRumble
        if( !input.val()  ) {
            input.attr('placeholder', 'type something!');
            var timeout;
            clearTimeout(timeout);
            form.trigger('startRumble');
            timeout = setTimeout(function(){form.trigger('stopRumble');}, 500);
            return false;
        }
        else {
            show_loading_overlay();
            return true;
        }
} 

/*
 * show_loading_overlay is called when a search query is entered or a .load-on-click is clicked.
 * It displays the #loading-overlay.
 * The code is a bit funky to ensure compatibility with safari's rendering engine, the solution was found:
 * http://stackoverflow.com/questions/14149038/jquery-show-function-is-not-executed-in-safari-if-submit-handler-returns-true
 */
function show_loading_overlay() {
    
    var verbs = ['calibrating', 'fueling', 'enlarging', 'charging', 'locking', 'acquiring', 'degaussing',
             'recalculating', 'spinning up', 'releasing', 'enumerating', 'starting', 'testing', 'mounting',
             'compiling', 'linking', 'connecting', 'deleting', 'fabricating', 'upgrading', 'looping'];
    
    var adjectives = ['big', 'tiny', 'flashing', 'required', 'tired', 'shiny', 'sparkling', 'radiant', 'spline',
                  'laser', 'cached', 'plasma', 'lava', 'fast', 'slow'];
    
    var nouns = ['server', 'capacitors', 'circuits', 'batteries', 'hamster', 'gerbil', 'music', 'electrodes',
             'RAM', 'CPU', 'goatherd', 'disk', 'conductor', 'prototypes', 'future', 'ozone', 'cloud',
             'screen', 'universe', 'loop'];

    $('#loading-message').text(function() {
        var verb = verbs[Math.floor(Math.random() * verbs.length)];
        var adjective = adjectives[Math.floor(Math.random() * adjectives.length)]; 
        var noun = nouns[Math.floor(Math.random() * nouns.length)];
        return verb + " " + adjective + " " + noun + "...";
    });
	var show_loading = function() { $('#loading-overlay').show(); };
    setTimeout(show_loading, 0);
}
  
/*
 * Once the rest of the document has loaded, prepare the autocomplete feature for the search boxes.
 */  
$(document).ready(function(){
	
	$('.load-on-click').click(function() {
            show_loading_overlay();
        });
	
    $.get( "/search_tags/", function( data ) {
        $( ".search" ).autocomplete({
            appendTo: "#someElem", 
            minLength: 2, 
            source: data.tags, 
            delay: 200,
            select : function(event, ui){ 
                        $(".search").val(ui.item.label);
                        show_loading_overlay();
                        /* 
                         * The autocomplete suggestions already exist in the database so we can direct
                         * straight to the show page for the selected entry. Have to replace spaces with
                         * underscores and all uppercase to lowercase.
                         */
                        var url_string = ui.item.label.toLowerCase();
                        url_string = url_string.replace(/[^\w\s]|_/g, "")
                        url_string = url_string.split(' ').join('_');
                        window.location.replace("/show/" + url_string); 
                    }
                });
    });
});
