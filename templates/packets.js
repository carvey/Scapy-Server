
/*
    The Django channels project does not yet have a frontend websocket wrapper, so this script was taken from
    https://github.com/andrewgodwin/channels-examples/blob/master/databinding/templates/index.html and adapted
    to work with this project
 */

var socket;

$(function () {
    // Correctly decide between ws:// and wss://
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + "/packets/stream/";
    console.log("Connecting to " + ws_path);
    socket = new ReconnectingWebSocket(ws_path);

    // Handle incoming messages
    socket.onmessage = function(message) {
        // Decode the JSON
        console.log("Got message " + message.data);
        var data = JSON.parse(message.data);
        var streamName = data.stream;
        var payload = data.payload;
        var table_body = $("#packets-table tbody");

        if (streamName == "pkts") {
            // Handle different actions
            if (payload.action == "create") {

                var row_count = document.getElementById('packets-table').rows.length;

                var new_row = "<tr data-value-id='" + payload.pk + "'>";
                new_row += "<td class='counter'>" + row_count + "</td>";
                new_row += "<td class='src_mac'>" + payload.src_mac + "</td>";
                new_row += "<td class='dst_mac'>" + payload.dst_mac + "</td>";
                new_row += "<td class='src_ip'>" + payload.src_ip + "</td>";
                new_row += "<td class='dst_ip'>" + payload.dst_ip + "</td>";
                new_row += "<td class='proto'>" + payload.proto + "</td>";
                new_row += "<td class='summary'>" + payload.summary + "</td>";
                new_row += "</tr>";

                table_body.append(new_row);


            } else if (payload.action == "update") {
                $("p[data-value-id=" + payload.pk + "] .src").text(payload.src);
                $("p[data-value-id=" + payload.pk + "] .dst").val(payload.dst);
                $("p[data-value-id=" + payload.pk + "] .proto").val(payload.proto);
                $("p[data-value-id=" + payload.pk + "] .summary").val(payload.summary);


            } else if (payload.action == "delete") {
                $("tr[data-value-id=" + payload.pk + "]").remove();


            } else {
                console.log("Unknown action " + payload.action);
            }
        } else {
            console.log("Unknown stream " + streamName);
        }
    };

    // Helpful debugging
    socket.onopen = function() {
        console.log("Connected to notification socket");
        socket.send(
            JSON.stringify({
                "stream": "web-connect",
                "payload": {
                    "connect": true
                }
            })
        );

    };
    socket.onclose = function() { console.log("Disconnected to notification socket"); }

});

$("#btn-clear").click(function() {

    $.ajax({
        url: "http://" + window.location.hostname + ":" + window.location.port + "/clear/"
    });

});

$("#btn-capture").click(function() {

    var scapy_filter = $("#scapy-filter").val();
    var device = $("#device-value").val();
    var count = parseInt(document.getElementById('capture-count').value);

    console.log(scapy_filter);

    if (device == null) {
        alert("Connect a remote device to capture from before attempting to capture");
        return;
    }

    if (!count) {
        alert("Enter a number of packets to capture");
        return;
    }

    scapy_filter = scapy_filter ? scapy_filter : null;

    socket.send(JSON.stringify({
        "stream": "capture",
        "payload": {
            "data": {
                "scapy_filter": scapy_filter,
                "capture": true,
                "device": device,
                "count": count
            }
        }
    }));

});