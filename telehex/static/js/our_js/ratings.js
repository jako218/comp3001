/*
 * ratings.js is the javascript used to create the ratings graphs for a particular show.
 * It works by getting a shows rating data from an AJAX call. This call returns a JSON object
 * which holds the ratings. The graphs are created using the d3 jQuery graphing library.
 */

/*
 * Waits for the page to load before creating the ratings graphs
 */
$(document).ready(function () {
    createRatingsGraphs();
});

/*
 * The CreateRatingsGraph function creates bar charts using the d3 jquery 
 * graphing library. Each bar chart is a season, with the ratings for each
 * episode of that season being displayed on the bar chart 
 */

function createRatingsGraphs() {
    // Specify margins for the main barchart component
    // Need margins so we can add axis labels and chart titles
    var margin = {
        top: 80,
        right: 10,
        bottom: 50,
        left: 50
    };

    // Calculate the width and the height of each bar chart
    var width = 960 - margin.left - margin.right,
        height = 430 - margin.top - margin.bottom;

    // Specify the scale of the x and y axis, the y goes from 0-10 as ratings can go from 0-10
    var xScale = d3.scale.ordinal().rangeRoundBands([0, width], 0.1);
    var yScale = d3.scale.linear().domain([0, 10]).range([height, 0]);

    // Create a pair of axis
    var xAxis = d3.svg.axis().scale(xScale).orient("bottom");
    var yAxis = d3.svg.axis().scale(yScale).orient("left");

    // Create a new tooltip which will be displayed on hover
    var tip = d3.tip().attr('class', 'd3-tip').offset([-20, 0]).html(function (d) {
        return "<em>" + d.name + "</em><br><strong>Rating:</strong> <span style='color:#c0392b'>" + d.rating + "</span>";
    });

    // Obtain the show slug so a ajax request can be performed
    var show_slug = $("#show_slug").text();

    // Obtain the JSON data, and generate the bar charts from this data
    d3.json("/data/ratings/").header("X-CSRFToken", $.cookie('csrftoken')).post("show_slug=" + show_slug, function (error, data) {
        // Create a list of seasons in descending order
        var seasons = d3.keys(data.shows).sort(function (a, b) {
            return b - a;
        });

        // For each season create a bar chart
        for (var season = 0; season < seasons.length; season++) {
            createBarChart(data, seasons, season);
        }
    });

    /*
     * The createBarChart Function creates a bar chart for a specific season in a TVShow
     * It takes data, which is a dictionary containing show objects and a list of seasons
     * which contains the episodes with their ratings. Keys is a list containing an ordered
     * list of seasons numbers and seasons specifies for which season the bar chart should be
     * constructed
     */
    function createBarChart(data, keys, season) {
        // Get the episodes in this season
        var episodes = data.shows[keys[season]];

        // Get the season number of this season
        var series_num = keys[season];

        // Obtain from the data which seasons have no ratings and put them in a set
        var no_ratings = d3.set(data.no_ratings);

        xScale.domain(episodes.map(function (d) {
            return d.episode;
        }));

        // Append a new bar chart container onto the end of the #ratingsgraphs container
        var chartclass = "season_" + series_num;
        var svg = d3.select("#ratingsgraphs").append("div").attr("id", chartclass).attr("class", "row graph");
        svg = d3.select("#" + chartclass)
            .append("svg").attr("width", width + margin.left + margin.right).attr("height", height + margin.top + margin.bottom)
            .append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var bar = svg.selectAll("g").data(episodes).enter().append("g").attr("transform", function (d) {
            return "translate(" + xScale(d.episode) + ", 0)";
        });

        // Add the tooltip
        svg.call(tip);

        // For each rating add a bar to the bar chart and add a mouseover event to display the relevant tooltip
        bar.append("rect").attr("class", ".bar").attr("y", function (d) {
            return yScale(d.rating);
        }).attr("height", function (d) {
            if (d.rating < 0) {
                return 0;
            } else {
                return height - yScale(d.rating);
            }
        }).attr("width", xScale.rangeBand()).attr("fill", "#c0392b").attr("onclick", function (d) {
            return "window.location.href='" + d.url + "';";
        }).on('mouseover', tip.show).on('mouseout', tip.hide);

        // Add the axes
        svg.append("g").attr("class", "x axis").attr("transform", "translate(0," + height + ")").call(xAxis);
        svg.append("g").attr("class", "y axis").call(yAxis);

        // Add the relevant text, x-label, y-label, etc. to the bar chart
        svg.append("text").attr("class", "x label").attr("text-anchor", "middle").attr("x", width / 2).attr("y", height + 40).text("Episode");
        svg.append("text").attr("class", "y label").attr("text-anchor", "middle").attr("y", -35).attr("x", 0 - (height / 2)).attr("transform", "rotate(-90)").text("Rating");
        svg.append("text").attr("class", "title label").attr("text-anchor", "middle").attr("y", -50).attr("x", 0 + margin.left).text("Season " + series_num);
        if (no_ratings.has(series_num)) {
            svg.append("text").attr("class", "noratings label").attr("text-anchor", "middle").attr("x", width / 2).attr("y", height / 2).text("No Ratings Available");
        }
    }
}