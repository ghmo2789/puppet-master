
var map = L.map('mapid').setView([60, 10], 3);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
              maxZoom: 19,
              attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                }).addTo(map);

var jsonData = JSON.parse(document.querySelector('#jsonData').getAttribute('data-json'));
var locations = jsonData.locations;
var greenIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});
var blueIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

function markerActivate(marker) {
  marker.myJsonData.checked = true;
  marker.setIcon(greenIcon);
}

function markerDeactivate(marker) {
  marker.myJsonData.checked = false;
  marker.setIcon(blueIcon);
}

let markers = [];

for (const clientLocation of locations) {
  var ids = clientLocation.client_ids;
  var loc = clientLocation.location;
  var marker = L.marker(loc).addTo(map).on('click', 
      function(e){
        var clickedMarker = e.target;
        var checked = clickedMarker.myJsonData.checked;
        
        // Fix marker color and status
        if (!checked) {
          markerActivate(clickedMarker)
        }
        else {
          markerDeactivate(clickedMarker)
        }

        // Fix checkboxes
        c_ids = clickedMarker.myJsonData.clientIds
        for (i = 0; i < c_ids.length; i++){
          var c_id = c_ids[i];
          let c_id_element = document.getElementById(c_id)
          if (c_id_element != null) {      
            if (!checked) {
              c_id_element.checked = true;
            }
            else {
              c_id_element.checked = false;
            }
          }
          toggleSubmit();
        }
      }
  );
  marker.myJsonData = {clientIds: ids,
                       checked: false};
  markers.push(marker)
}

function toggleMarker() {
  for (i = 0; i < markers.length; i++) {
    var marker = markers[i];
    var c_ids = marker.myJsonData.clientIds;
    var client_checked = false;
    
    for (j = 0; j < c_ids.length; j++) {
      c_id = c_ids[j];
      let c_id_element = document.getElementById(c_id); 
      if (c_id_element != null && c_id_element.checked) {
        client_checked = true;
      }
    }
    if (client_checked) {
      markerActivate(marker);
    }
    else {
      markerDeactivate(marker);
    }
  }
}