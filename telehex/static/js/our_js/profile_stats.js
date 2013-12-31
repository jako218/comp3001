/*
 * profile_stats.js is the JavaScript for generating the graphs on the profile_stats.html page.
 * The javascript creates 3 pie charts and one partion layout graph, created from the d3 graphing
 * library. The 3 pie charts make use of CSV and make AJAX request to get this data, whereas the 
 * partion layout graph makes use of JSON, again requested throughn and AJAX request.
 */

$(document).ready(function(){
    // Create the 3 pie charts when the document is finished loading
    createPieChart("../stats_pie_genre", "#genre_pie", "genre");
    createPieChart("../stats_pie_ratings", "#ratings_pie", "rating");
    createPieChart("../stats_pie_status", "#status_pie", "status");
    
    // Create the partion layout graph
    createPartionLayout();
});

/*
 * The createPieChart function takes a url to retrieve the csv data from,
 * a css selector for where to place the pie chart, and specifies an attribute
 * which accesses the correct column of data from a csv file, for example, 'genre'
 * would get the value specified in the genre column. It then makes use of the 
 * extensive function specified in the d3 graphing library to create a pie chart
 */
function createPieChart(url, selector, attribute){
    var width = 250,
        height = 250,
        radius = Math.min(width, height) / 2;

    // Colours are an ordinal scale that map an input to an output
    // If there are fewer elements in the range than the domain, values are recycled
    var colour = d3.scale.ordinal().range(["#e74c3c", "#34495e", "#2980b9", "#c0392b", "#3498db", "#2c3e50", "#ecf0f1"]);

    // Create a new arc generator
    var arc = d3.svg.arc().outerRadius(radius - 10).innerRadius(0);

    // Creates a new pie function layout, with sorting disables
    // The size of the data is extracted for the pie chart
    var pie = d3.layout.pie().sort(null).value(function (data) {
        return data.Size;
    });

    // Function to generate the genre pie chart, takes a CSV object
    var svg = d3.select(selector).append("svg").attr("width", width).attr("height", height)
        .append("g").attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    // Make a CSV object from the data found at url, which is created in views.py
    d3.csv(url, function (error, data) {

        // Loop through each row of the csv file
        data.forEach(function (d) {
            // Convert "size" column to number
            d.Size = +d.Size;
        });

        // Select all the arcs and join them with the pie chart data
        // Append the 'g', group object, with a class of arc to the selection
        var genre_graph = svg.selectAll(".arc").data(pie(data)).enter().append("g").attr("class", "arc");

        genre_graph.append("path").attr("d", arc).style("fill", function (d) {
            // Return a colour based on the genre
            return colour(d.data[attribute]);
        });

        // Add the pie chart text 
        genre_graph.append("text").attr("transform", function (d) {
            // Specify the locaiton of the text
            return "translate(" + arc.centroid(d) + ")";
        }).attr("dy", ".25em").style("text-anchor", "middle").text(function (d) {
            // Specify the text 
            return d.data[attribute];
        }).attr("color", "#fff");
    });
}

/*
 * The createPartionLayout creates a d3 graph which displays the user's shows ordered by the season
 * with the highest average rating. The function makes a AJAX JSON request to obtain the data and is 
 * clickable so certain parts of the graph can be made bigger.
 */
function createPartionLayout() {
    var w = 1120,
        h = 1000,
        x = d3.scale.linear().range([0, w]),
        y = d3.scale.linear().range([0, h]);

    // Select the div called layout graph and append additional divs to place the partion layout graph
    var vis = d3.select("#layout_graph")
        .append("div").attr("class", "chart tree_center colour_change").style("width", w + "px").style("height", h + "px")
        .append("svg:svg").attr("width", w).attr("height", h);

    // Construct a partition layout object, with the values to construct the graph 
    // specifed by the ratings for each data item
    var partition = d3.layout.partition().value(function (d) {
        return d.rating;
    });

    // Make a JSON object from the data found at /stats_data, created in views.py
    d3.json("../stats_data", function (root) {
        
        // Create a new partition layout graph and specify the position of the rectangles
        // Also add an action for when a rectangle is clicked
        var graph = vis.selectAll("g").data(partition.nodes(root)).enter().append("svg:g")
            .attr("transform", function (d) {
                return "translate(" + x(d.y) + "," + y(d.x) + ")";
            })
            .on("click", click);

        // Specify a kx and ky used to position the individual rectangles and text
        var kx = w,
            ky = h;

        // Specify an initial width and height of a rectangle and set its colour based on 
        // whether it has any children
        graph.append("svg:rect").attr("width", root.dy * kx).attr("height", function (d) {
            return d.dx * ky;
        }).attr("class", function (d) {
            return d.children ? "parent colour_change" : "child colour_change";
        });

        // Specify the intial position of the text in the rectangles
        graph.append("svg:text").attr("transform", transform).attr("dy", ".35em").style("opacity", function (d) {
            // Specify whether the text is display based on the height of the rectangle
            return d.dx * ky > 12 ? 1 : 0;
        }).text(function (d) {
            // Return the text of show/episode
            return d.name;
        });

        // If any part of the window is clicked change the partion graph to display the root
        d3.select(window).on("click", function () {
            click(root);
        });

        // When a rectangle is clicked zoom in a specific part of the graph containing that rectangle
        function click(d) {
            // if the node then return as the graph cannot be zoomed any further
            if (!d.children) {
                d3.event.stopPropagation();
                return;
            }

            // Specify the new positions for the rectangles
            kx = (d.y ? w - 40 : w) / (1 - d.y);
            ky = h / d.dx;
            x.domain([d.y, 1]).range([d.y ? 40 : 0, w]);
            y.domain([d.x, d.x + d.dx]);

            // Create a new transition that takes 750 ms and translates the rectangles
            var t = graph.transition().duration(750).attr("transform", function (d) {
                return "translate(" + x(d.y) + "," + y(d.x) + ")";
            });

            // Specify a new width and height for the rectangles
            t.select("rect").attr("width", d.dy * kx).attr("height", function (d) {
                return d.dx * ky;
            });

            // Move the text in the rectangles
            t.select("text").attr("transform", transform).style("opacity", function (d) {
                return d.dx * ky > 12 ? 1 : 0;
            });

            d3.event.stopPropagation();
        }

        /*
         * A Function which moves an object using the html canvas translate method
         */
        function transform(d) {
            return "translate(10," + d.dx * ky / 2 + ")";
        }

    });
}