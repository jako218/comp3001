/*
 * The similarity.js file is used to create a similarity tree. It makes use
 * of the d3 jquery graphing library. In order to construct the similairty 
 * tree an AJAX request is made for a JSON object containing the data required
 * to construct the tree. The JSON object is created using a recursive function
 * in the views.py file.
 */

/*
 * Waits for the page to load before creating the similarity graph
 */
$(document).ready(function () {
    createSimilarityGraph();
});

/*
 * The createSimilarityGraph function creates a clickable tree graph
 * which can be used to display 
 */
function createSimilarityGraph() {
    
    var id = 0,
        width = 980,
        height = 800,
        root;

    // Create a new d3 tree object
    var tree = d3.layout.tree().size([width, height]);

    // Create a new projection requied for transitions when a node is clicked
    var diagonal = d3.svg.diagonal().projection(function (d) {
        return [d.x, d.y];
    });

    // Select the #graph container and create a new svg component so a similarity
    // graph can be created 
    var similarity_graph = d3.select("#similarity-graph")
        .append("svg:svg").attr("width", width).attr("height", height)
        .append("svg:g").attr("transform", "translate(0, 100)");

    // Get the key name of the show which is used in the ajax request for the JSON
    // object used to hold the similarity data
    var show_key_name = $("#show_key_name").text();

    // Get the json similarity data
    d3.json("/data/similarity/").header("X-CSRFToken", $.cookie('csrftoken')).post("show_id=" + show_key_name, function (error, data) {

        // Set the root node of the tree to be the root of the json data
        root = data;

        // Set where the root node is positioned
        root.x0 = width / 2;
        root.y0 = 0;

        // Toggle whether or not a node is displayed
        function toggleAll(node) {
            if (node.children) {
                node.children.forEach(toggleAll);
                toggle(node);
            }
        }

        // Display the children of the root node if they exist
        root.children.forEach(toggleAll);

        // Update the graph from the root node
        update(root);
    });

    function update(source) {
        // Set the duration of the transitions - set to 300ms
        var duration = 300;

        // Runs tree layout and return array of nodes associated with root
        var nodes = tree.nodes(root).reverse();

        // Specify where each node appears based on its depth
        nodes.forEach(function (d) {
            d.y = d.depth * 150;
        });

        // Select all the nodes and update them
        var node = similarity_graph.selectAll("g.node").data(nodes, function (d) {
            // Return the id or create it if it's not been set
            return d.id || (d.id = ++id);
        });

        // Enter any new nodes at the parent's previous position.
        var nodeEnter = node.enter().append("svg:g").attr("class", "node").attr("transform", function (d) {
            return "translate(" + source.x0 + "," + source.y0 + ")";
        });

        // Specify the width of the hexagon when it is hidden
        var hex_width = 1e-6;
        var hex_height = Math.sqrt(3) / 2 * 1e-6;

        // Create a new hexagon polygon
        nodeEnter.append("svg:polygon").attr("points", [
            [hex_width, 0],
            [hex_width / 2, hex_height],
            [-hex_width / 2, hex_height],
            [-hex_width, 0],
            [-hex_width / 2, -hex_height],
            [hex_width / 2, -hex_height]
        ]);

        // Add an image to the node and set a click event which makes it show its children if it has any
        nodeEnter.append("svg:image").attr("xlink:href", function (d) {
            return d.imagelink;
        }).attr("width", 1e-6).attr("height", 1e-6).attr("transform", "translate(-50, -50)").on("oncontextmenu", function (d) {
            window.location = "/show/" + d.url;
        }).on("click", function (d) {
            toggle(d);
            update(d);
        });

        // Append a hyperlink to a shows page above the node for that show
        nodeEnter.append("svg:a").attr("xlink:href", function (d) {
            return "/show/" + d.url;
        }).append("svg:text").attr("x", "0").attr("dy", "-50").attr("text-anchor", "middle").text(function (d) {
            return d.name;
        }).style("fill-opacity", 1e-6);

        // Move the hexagon nodes to their new positions
        var nodeUpdate = node.transition().duration(duration).attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        });

        // Specify the size of a hexagon when being displayed
        hex_width = 50;
        hex_height = Math.sqrt(3) / 2 * hex_width;

        // Show these hexagons when a parent node is clicked to display them
        nodeUpdate.select("polygon").attr("points", [
            [hex_width, 0],
            [hex_width / 2, hex_height],
            [-hex_width / 2, hex_height],
            [-hex_width, 0],
            [-hex_width / 2, -hex_height],
            [hex_width / 2, -hex_height]
        ]).style("stroke", function (d) {
            // If a node has children set its border colour to #c0392b (red), otherwise white
            return d._children ? "#c0392b" : "#fff";
        });
        nodeUpdate.select("image").attr("width", 100).attr("height", 100);
        nodeUpdate.select("text").style("fill-opacity", 1);

        // When nodes are being removed move them to their parents position
        var nodeExit = node.exit().transition().duration(duration/2).attr("transform", function (d) {
            return "translate(" + source.x + "," + source.y + ")";
        }).remove();

        // Specify the size of a hexagon node when they are destroyed
        hex_width = 1e-6;
        hex_height = Math.sqrt(3) / 2 * hex_width;

        // Change the size of the hexagon on exit
        nodeExit.select("polygon").attr("points", [
            [hex_width, 0],
            [hex_width / 2, hex_height],
            [-hex_width / 2, hex_height],
            [-hex_width, 0],
            [-hex_width / 2, -hex_height],
            [hex_width / 2, -hex_height]
        ]);
        nodeExit.select("image").attr("width", 1e-6).attr("height", 1e-6).attr("transform", "translate(-50, -50)");

        // Create the connections between the nodes
        var connections = similarity_graph.selectAll("path.connection").data(tree.links(nodes), function (d) {
            return d.target.id;
        });

        // Any new connections are created at their parents position
        connections.enter().insert("svg:path", "g").attr("class", "connection").attr("d", function (d) {
            var o = {
                x: source.x0,
                y: source.y0
            };
            return diagonal({
                source: o,
                target: o
            });
        }).transition().duration(duration).attr("d", diagonal);

        // Move the connections to their new positions
        connections.transition().duration(duration).attr("d", diagonal);

        // Remove connections
        connections.exit().remove();

        // Store the old positions so they can be used in later transitions
        nodes.forEach(function (d) {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    }

    /*
     * A function which is used to toggle the childen,
     * which determines whether or not they are displayed
     */
    function toggle(d) {
        if (d.children) {
            d._children = d.children;
            d.children = null;
        } else {
            d.children = d._children;
            d._children = null;
        }
    }
}
