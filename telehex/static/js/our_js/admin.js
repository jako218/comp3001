/*
 * admin.js holds the javascript for the admin page. Makes use of the 
 * table sorter jQuery plugin to provide a sortable table.
 */

// When the document is loaded added a table sorter to the scraped shows table
$(document).ready(function() {
    $('#scraped-table').tablesorter({
        // Don't sort the 4th column
        headers: { 4: { sorter: false } },
        // Tell the sorter to sort the second column in ascending order
        sortList: [[1,0]]
    });
});
