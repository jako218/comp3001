/*
 * calendar.js holds the javascript for the calendar page. Makes use of the
 * fullCalendar jQuery plugin to construct a calendar from JSON event objects
 * which are gotten using ajax GET request. Also handles whether or not a 
 * user is subscribed to receiving email updates.
 */

$(document).ready(function() {

    // Create the calendar
    $('#calendar').fullCalendar({
        // Use the jQuery UI theming
        theme: true,
        header: {left: 'prev,next today', center: 'title', right: 'month,basicWeek'},
        
        // Specify where to get the calendar data from - uses AJAX to get a JSON
        // object of calendar events
        events: "/data/calendar/",
        firstDay: 1,
        weekMode: "variable",
        
        // Fade past events out on the calendar
        eventRender: function(calevent, element) {
            var currentDate = new Date();
            currentDate.setDate(currentDate.getDate() - 1);
            if(calevent.start.getTime() < currentDate)
                element.addClass("oldclass");
        }
	});

});
