function callRest(url, callback){
    var xmlhttp;
    // compatible with IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200){
            callback(xmlhttp.responseText);
        }
    }
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

function loadData() {
    callRest("/current_status", function(data) {
        showCurrentTemperatureData(JSON.parse(data));
    });

    for (var i = 1; i < 5; i++) {
        var placeholder = '<div class="col-md-6" ><div class="panel"><header><h2 id="room-title-' + i + '"></h2></header><div id="room-' + i + '"></div></div>';
        document.getElementById("graphs").innerHTML += placeholder;

        callRest("/graph/" + i, function(data) {
            showGraph(JSON.parse(data));
        })
    }
}

function showCurrentTemperatureData(data) {
    var html = '';
    for (var room in data) {
        if (data.hasOwnProperty(room)) {

            html += '<div class="col-xs-12 col-sm-6 col-md-3"><div class="panel">';
            html += '<header><h2>' + room + '</h2></header>';
            html += '<main><h3>';
            html += data[room].temperature + '<sub>&deg;C</sub>';

            if (data[room].humidity) {
                html += ' / ' + data[room].humidity + '<sub>%</sub>';
            }

            html += '</h3></main>';
            html += '<footer><time>' + data[room].time + '</time> / Battery: ' + data[room].battery + '</footer>';
            html += '</div></div>';
        }
    }

    document.getElementById("current-status").innerHTML = html;
}

function showGraph(data) {
    // Convert data into proper format
    var x = [];
    var t = [];
    var h = [];

    for (var datapoint in data.data) {
        if (data.data.hasOwnProperty(datapoint)) {
            x.push(data.data[datapoint].time);
            t.push(data.data[datapoint].temperature);

            if (data.data[datapoint].humidity) {
                h.push(data.data[datapoint].humidity);
            }
        }
    }

    var graph_data = [
        {
            x: x,
            y: t,
            name: 'Temperature',
            type: 'area'
        }];

    var room_id = data["room_id"];

    var range;
    if (room_id == 1) {   // outside
        range = [-10, 40]
    } else {
        range = [5, 30]
    }

    var layout = {
        paper_bgcolor: '#00000000',
        height: 300,
        showlegend: false,
        yaxis: {
            title: 'Temperature',
            range: range,
            hoverformat: '.2f C',
            zeroline: false
        }
    };

    // Humidity data may be missing
    if (h.length > 0) {
        graph_data.push(
        {
            x: x,
            y: h,
            name: 'Humidity',
            yaxis: 'y2',
            type: 'scatter',
            fill: 'tonexty'
        });

        layout["yaxis2"] = {
                title: 'Humidity',
                titlefont: {color: 'rgb(148, 103, 189)'},
                tickfont: {color: 'rgb(148, 103, 189)'},
                overlaying: 'y',
                side: 'right',
                range: [0, 100],
                zeroline: false
        }
    }

    document.getElementById("room-title-" + room_id).innerHTML = data.room;
    Plotly.setPlotConfig({ logging: 2 });
    Plotly.newPlot('room-' + room_id, graph_data, layout);
}