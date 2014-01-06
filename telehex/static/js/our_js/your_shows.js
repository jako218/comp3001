/*
 * profile.js holds the javascript for the profile page. The javascript is used to
 * calculate the days until the next episode of a show airs, or if it doesn't exist
 * is used displays, ended, on-hiatus, etc. The JavaScript is also used to resize
 * the font size to ensure that the site remains as responsive as possible
 */


/*
 * The daysUntil function works out the number of days from today to the date string
 * passed into the function.
 */
function daysUntil(dateString) {
    if (dateString === "") return "";
    var now = Date.parse(new Date().toDateString()),
        dateEnd = Date.parse(dateString),
        days = (dateEnd - now) / 1000 / 60 / 60 / 24; // convert milliseconds to days
    return days;
}

/* Check the width of the window, if a particular size than a certain size reduce days left font size
 * otherwise reset so the default values are used
 */
function changeDaysLeftFontSize() {
    if ($(window).width() < 976 && $(window).width() > 752) $('.days-left').css({
        "font-size": "20px",
        "top": "35%"
    });
    else $('.days-left').css({
        "font-size": "",
        "top": ""
    });
}

// Wait until the document is loaded before doing any jQuery
$(document).ready(function () {
    changeDaysLeftFontSize();

    // Change the days-left font size when the window is resized
    $(window).resize(function () {
        changeDaysLeftFontSize();
    });

    // Get all the hex-images with airdates
    var images = $(".hex-im-cont").children(".airdate");

    // For each hex-image work out the day until it next airs and append this to the string in the hover
    images.each(function () {
        var daysleft = daysUntil($(this).text());
        if (daysleft === 0) $(this).siblings(".days-left").text("Today");
        else if (daysleft === 1) $(this).siblings(".days-left").text("Tomorrow");
        else $(this).siblings(".days-left").append(daysleft + " days!");

        $(this).siblings(".days-left").hide();
    });

    // Specify a function that gets executed on hex-image hover
    $(".hex-im").hover(function () {
        // Image is being hovered over - add the hover class
        $(this).addClass("hover_hex");
        // Show the days left
        $(this).parent().siblings(".days-left").show();
    }, function () {
        // Image is being left 
        $(this).removeClass("hover_hex");
        $(this).parent().siblings(".days-left").hide();
    });

    // Function to prevent flickering when days left div is hovered over
    $(".days-left").hover(function () {
        $(this).siblings("a").children(".hex-im").mouseenter();
    }, function () {
        $(this).siblings("a").children(".hex-im").mouseleave();
    });

    // Using the iCheck plugin, style the email checkbox
    $('input').each(function(){
        var self = $(this),
        label = self.next(),
        label_text = label.text();

        label.remove();
        self.iCheck({
            checkboxClass: 'icheckbox_line-blue',
            insert: '<div class="icheck_line-icon"></div>' + '<span id="subscribelabel">' + label_text + '</span>'
        });
    }); 

    // Having the checkbox 'checked' for receive_updates == false and
    // unchecked for receive_updates == true means we get a tick when
    // the user isn't subscribed (to prompt them to subscribe) and a 
    // cross when they are (to prompt them to unsubscribe)

    // If unchecked, user has subscribed 
    $("#updates_check").on('ifUnchecked', function(event){
        $.get("/receive_updates/");
        $("#subscribelabel").text("Stop Receiving Email Updates");
        $("#subscribeoffer").text("You will receive a weekly email on Sundays, summarising the coming week's shows.");
    });
   
    // If checked, user has unsubscribed
    $("#updates_check").on('ifChecked', function(event){
        $.get("/receive_updates/");
        $("#subscribelabel").text("Receive Email Updates");
        $("#subscribeoffer").text("Would you like us to email you a weekly summary of the coming week's shows?");
    });
});
