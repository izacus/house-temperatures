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
}

function showCurrentTemperatureData(data) {
    var html = '';
    for (var room in data) {
        if (data.hasOwnProperty(room)) {

            html += ' <div class="col-xs-12 col-sm-6 col-md-3"><div class="panel">';
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