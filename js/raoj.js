var width = 750,
    height = 750;

var color = d3.scale.ordinal()
    .domain(["Reader", "Romeo", "Juliet", "Nurse", "R&J",
        "Rosaline", "Puck", "Macbeth", "P&T"])
    .range(["#FFFFFF", "#CD3E38", "#FACBC5", "#C37873", "#984B45",
        "#521711", "AEE2CC", "#AEE2CC", "#AEE2CC"]);

var force = d3.layout.force()
    .charge(-50)
    .gravity(.175)
    .size([width, height]);

var svg = d3.select(".graph-sec").append("svg")
    .attr("class", "graph")
    .attr("width", width)
    .attr("height", height)
    .append("g");

var container = svg.append("g");

d3.json("./json/RaoJ.json", function (error, graph) {
    if (error) throw error;

    force
        .nodes(graph.nodes)
        .links(graph.links)
        .start();

    svg.append("svg:defs").selectAll("marker")
        .data(["end", "bard_end"])      // Different link/path types can be defined here
        .enter().append("svg:marker")    // This section adds in the arrows
        .attr("id", String)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 13)
        .attr("refY", 0)
        .attr("markerWidth", 3)
        .attr("markerHeight", 3)
        .attr("orient", "auto")
        .attr("fill", function (d) { return d === "end" ? "#FFFFFF" : "#CD3E38" })
        .append("svg:path")
        .attr("d", "M0,-5L10,0L0,5");

    // add the links and the arrows
    var path = container.append("svg:g").selectAll("path")
        .data(graph.links)
        .enter().append("svg:path")
        .attr("class", "link")
        .attr("stroke", function (d) { return d.bard_choice ? "#CD3E38" : "#FFFFFF" })
        .attr("marker-end", function (d) { return d.bard_choice ? "url(#bard_end)" : "url(#end)" });

    path.append("title")
        .text(function (d) { return d.description; });

    var node = container.selectAll(".node")
        .data(graph.nodes)
        .enter().append("circle")
        .attr("class", "node")
        .attr("r", function (d) {
            if (d.is_ending) {
                return 6;
            } else if (d.id == 'Cover' || d.id == 'THE END FOR REAL THIS TIME') {
                return 12;
            } else {
                return 3;
            }
        })
        .style("fill", function (d) { return color(d.pov); })
        .call(force.drag);

    node.append("title")
        .text(function (d) { return d.id + ": " + d.description + " (" + d.pov + ")"; });

    force.on("tick", function () {
        path.attr("d", function (d) {
            return "M" +
                d.source.x + "," +
                d.source.y + " " +
                d.target.x + "," +
                d.target.y;
        });

        node.attr("cx", function (d) { return d.x; })
            .attr("cy", function (d) { return d.y; });
    });
});
