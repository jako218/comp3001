// Common variables which are shared between all three pie charts
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

// Functions generate the proper closure to prevent the graphs from interferring 
(function () { 
    // Function to generate the genre pie chart, takes a CSV object
    var svg = d3.select("#genre_pie").append("svg").attr("width", width).attr("height", height)
        .append("g").attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    // Make a CSV object from the data found at /stats_data, created in views.py
    d3.csv("../stats_pie_genre", function (error, data) {

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
            return colour(d.data.genre);
        });

        // Add the pie chart text 
        genre_graph.append("text").attr("transform", function (d) {
            // Specify the locaiton of the text
            return "translate(" + arc.centroid(d) + ")";
        }).attr("dy", ".25em").style("text-anchor", "middle").text(function (d) {
            // Specify the text 
            return d.data.genre;
        }).attr("color", "#fff");
    });
})();

(function () { /* function to generate the ratings pie chart, takes a CSV object */
    var svg = d3.select("#ratings_pie").append("svg").attr("width", width).attr("height", height).append("g").attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    /* make a CSV object from the data found at /stats_data, created in views.py */
    d3.csv("../stats_pie_ratings", function (error, data) {

        data.forEach(function (d) {
            d.Size = +d.Size;
        });

        var g = svg.selectAll(".arc").data(pie(data)).enter().append("g").attr("class", "arc");

        g.append("path").attr("d", arc).style("fill", function (d) {
            return colour(d.data.rating);
        });

        /*add the pie chart text*/
        g.append("text").attr("transform", function (d) {
            return "translate(" + arc.centroid(d) + ")";
        }).attr("dy", ".25em").style("text-anchor", "middle").text(function (d) {
            return d.data.rating;
        });
    });
})();

(function () { /* function to generate the status pie chart, takes a CSV object */
    var svg = d3.select("#status_pie").append("svg").attr("width", width).attr("height", height).append("g").attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    /* make a CSV object from the data found at /stats_data, created in views.py */
    d3.csv("../stats_pie_status", function (error, data) {

        data.forEach(function (d) {
            d.Size = +d.Size;
        });

        var g = svg.selectAll(".arc").data(pie(data)).enter().append("g").attr("class", "arc");

        g.append("path").attr("d", arc).style("fill", function (d) {
            return colour(d.data.status);
        });

        /*add the pie chart text*/
        g.append("text").attr("transform", function (d) {
            return "translate(" + arc.centroid(d) + ")";
        }).attr("dy", ".25em").style("text-anchor", "middle").text(function (d) {
            return d.data.status;
        });
    });
})();

//for the partition layout d3 graph, shows the users shows ordered by the season scoring highest
(function () {
    var w = 1120,
        h = 1000,
        x = d3.scale.linear().range([0, w]),
        y = d3.scale.linear().range([0, h]);

    var vis = d3.select("#layout_graph").append("div").attr("class", "chart tree_center color_change").style("width", w + "px").style("height", h + "px").append("svg:svg").attr("width", w).attr("height", h);

    var partition = d3.layout.partition().value(function (d) {
        return d.size;
    });

    /* make a JSON object from the data found at /stats_data, created in views.py */
    d3.json("../stats_data", function (root) {
        var g = vis.selectAll("g").data(partition.nodes(root)).enter().append("svg:g").attr("transform", function (d) {
            return "translate(" + x(d.y) + "," + y(d.x) + ")";
        }).on("click", click);

        var kx = w / root.dx,
            ky = h / 1;

        g.append("svg:rect").attr("width", root.dy * kx).attr("height", function (d) {
            return d.dx * ky;
        }).attr("class", function (d) {
            return d.children ? "parent color_change" : "child color_change";
        });

        g.append("svg:text").attr("transform", transform).attr("dy", ".35em").style("opacity", function (d) {
            return d.dx * ky > 12 ? 1 : 0;
        }).text(function (d) {
            return d.name;
        });

        d3.select(window).on("click", function () {
            click(root);
        });

        /* append a graph zoom when any rectangle is clicked*/

        function click(d) {
            if (!d.children) return;

            kx = (d.y ? w - 40 : w) / (1 - d.y);
            ky = h / d.dx;
            x.domain([d.y, 1]).range([d.y ? 40 : 0, w]);
            y.domain([d.x, d.x + d.dx]);

            var t = g.transition().duration(d3.event.altKey ? 7500 : 750).attr("transform", function (d) {
                return "translate(" + x(d.y) + "," + y(d.x) + ")";
            });

            t.select("rect").attr("width", d.dy * kx).attr("height", function (d) {
                return d.dx * ky;
            });

            t.select("text").attr("transform", transform).style("opacity", function (d) {
                return d.dx * ky > 12 ? 1 : 0;
            });

            d3.event.stopPropagation();
        }

        function transform(d) {
            return "translate(8," + d.dx * ky / 2 + ")";
        }

    });
})();