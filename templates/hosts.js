
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

        if (streamName == "hosts") {
            // Handle different actions
            if (payload.action == "create") {
                var row_count = document.getElementById('packets-table').rows.length;

                var payload_options = $("#payload-options").children().clone(true, true);
                //payload_options.css('display', 'table-cell');

                var new_row = "<tr data-value-id='" + payload.pk + "'>";
                new_row += "<td class='counter'>" + row_count + "</td>";
                new_row += "<td class='mac'>" + payload.data.mac + "</td>";
                new_row += "<td class='ip'>" + payload.data.ip + "</td>";
                new_row += "<td class='payload-row'>" + "</td>";
                new_row += "</tr>";

                table_body.append(new_row);

                console.log(payload_options);
                console.log($("tr[data-value-id=" + payload.pk + "] .payload-row"));
                $("tr[data-value-id=" + payload.pk + "] .payload-row").append(payload_options);

            } else if (payload.action == "update") {
                $("p[data-value-id=" + payload.pk + "] .mac").text(payload.data.mac);
                $("p[data-value-id=" + payload.pk + "] .ip").text(payload.data.ip);

            } else if (payload.action == "delete") {
                $("tr[data-value-id=" + payload.pk + "]").remove();

            } else {
                console.log("Unknown action " + payload.action);
            }
        } else {
            console.log("Unknown stream " + streamName);
        }
    };

    socket.onopen = function() {
        console.log("Connected to hosts notification socket");
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

$(".btn-execute").click(function() {

    var parent = $(this).parents("tr");
    var payload = parent.find(".payloads").val();
    var mac = parent.find(".mac").html();
    var ip = parent.find(".ip").html();

    socket.send(JSON.stringify({
        "stream": "execute",
        "payload": {
            "data": {
                "payload": payload,
                "mac": mac,
                "ip": ip
            }
        }
    }));

});