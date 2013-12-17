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
            input.css({'border-color':'#c0392b', 'border-width':'2px'}).focus();
            //need to think of a way to return this back to normal at some point, cba right now
            var timeout;
            clearTimeout(timeout);
            form.trigger('startRumble');
            timeout = setTimeout(function(){form.trigger('stopRumble');}, 500);
                
            return false;
        }
        else {
            console.log(input);
            $('#loading-overlay').show();
            return true;
        }
} 
  
/*
 * Once the rest of the document has loaded, prepare the autocomplete feature for the search boxes.
 */  
$(document).ready(function(){
    $.get( "/search_tags/", function( data ) {
        $( ".search" ).autocomplete({
            appendTo: "#someElem", 
            minLength: 2, 
            source: data.tags, 
            delay: 200,
            select : function(event, ui){ 
                        $(".search").val(ui.item.label);
                        $('#loading-overlay').show();
                        /* 
                         * The autocomplete suggestions already exist in the database so we can direct
                         * straight to the show page for the selected entry. Have to replace spaces with
                         * underscores and all uppercase to lowercase.
                         */
                        var url_string = ui.item.label.toLowerCase(); 
                        url_string = url_string.split(' ').join('_');
                        window.location.replace("/show/" + url_string); 
                    }
                });
    });
});