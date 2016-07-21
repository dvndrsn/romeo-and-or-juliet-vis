var width = 750,
    height = 750;

var color = d3.scale.ordinal()
        .domain(["Reader", "Romeo",   "Juliet",  "Nurse",   "R&J",
                 "Rosaline", "Puck",   "Macbeth", "P&T"])
        .range(["#FFFFFF", "#CD3E38", "#FACBC5", "#C37873", "#984B45",
                "#521711",   "AEE2CC", "#AEE2CC", "#AEE2CC"]);

var force = d3.layout.force()
        .charge(-50)
        .gravity(.175)
        // .friction(.7)
        // .charge(-500)
        // .gravity(1.3)
        .size([width, height]);

var zoom = d3.behavior.zoom()
        .scaleExtent([.5, 10])
        .on("zoom", zoomed);

function zoomed() {
    container.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
}

function dragstarted(d) {
    d3.event.sourceEvent.stopPropagation();
    d3.select(this).classed("dragging", true);
}

function dragged(d) {
    d3.select(this).attr("cx", d.x = d3.event.x).attr("cy", d.y = d3.event.y);
}

function dragended(d) {
    d3.select(this).classed("dragging", false);
}

var svg = d3.select(".graph-sec").append("svg")
        .attr("class", "graph")
        .attr("width", width)
        .attr("height", height)
        .append("g");
        // .call(zoom);

var container = svg.append("g");


var drag = d3.behavior.drag()
        .origin(function(d) { return d; })
        .on("dragstart", dragstarted)
        .on("drag", dragged)
        .on("dragend", dragended);

d3.json("RaoJ.json", function(error, graph) {
    if (error) throw error;

    force
        .nodes(graph.nodes)
        .links(graph.links)
        .start();

    /* var link = svg.selectAll(".link") */
    /* .data(graph.links) */
    /* .enter().append("line") */
    /* .attr("class", "link") */
    /* .style("stroke-width", function(d) { return Math.sqrt(d.value); }) */
    /* .style("stroke", function(d) { return d.bard_choice ? "#CD3E38" : null}); //"#FFFFFF" }); */
    /*  */
    /* link.append("title") */
    /* .text(function(d) { d.description; }); */
    // build the arrow.

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
        .attr("fill", function(d) { return d === "end" ? "#FFFFFF" : "#CD3E38"})
        .append("svg:path")
        .attr("d", "M0,-5L10,0L0,5");

    // add the links and the arrows
    var path = container.append("svg:g").selectAll("path")
            .data(graph.links)
            .enter().append("svg:path")
    //    .attr("class", function(d) { return "link " + d.type; })
            .attr("class", "link")
            .attr("stroke", function(d) { return d.bard_choice ? "#CD3E38" : "#FFFFFF"})
            .attr("marker-end", function(d) { return d.bard_choice ? "url(#bard_end)" : "url(#end)"});

    path.append("title")
        .text(function(d) { return d.description; });

    var node = container.selectAll(".node")
            .data(graph.nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", function(d) {
                if (d.is_ending) {
                    return 6;
                } else if (d.id == 'Cover' || d.id == 'THE END FOR REAL THIS TIME') {
                    return 12;
                } else {
                    return 3;
                }
            })
            .style("fill", function(d) { return color(d.pov); })
            .attr("data-legend", function(d) { return d.pov; } )
            .attr("data-legend-color", function(d) { return color(d.pov); })
            .call(force.drag);

    node.append("title")
        .text(function(d) { return d.id + ": " + d.description + " (" + d.pov + ")"; });

    /* legend = svg.append("g") */
    /* .attr("class","legend") */
    /* .attr("transform","translate(50,30)") */
    /* .style("font-size","12px") */
    /* .call(d3.legend); */

    force.on("tick", function() {
        path.attr("d", function(d) {
            /* var dx = d.target.x - d.source.x, */
            /* dy = d.target.y - d.source.y, */
            /* dr = Math.sqrt(dx * dx + dy * dy); */
            return "M" +
                d.source.x + "," +
                d.source.y + " " + // "A" +
                /* dr + "," + dr + " 0 0,1 " + */
            d.target.x + "," +
                d.target.y;

        });
        /* link.attr("x1", function(d) { return d.source.x; }) */
        /* .attr("y1", function(d) { return d.source.y; }) */
        /* .attr("x2", function(d) { return d.target.x; }) */
        /* .attr("y2", function(d) { return d.target.y; }); */

        node.attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });

    });
});
