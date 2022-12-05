
function onMarkerClick(e){
  console.log('clicked marker: ' + e);
}

var map = L.map('mapid').setView([30, 0], 0.5);
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

for (const clientLocation of locations) {
  var id = clientLocation.client;
  var loc = clientLocation.location;
  var marker = L.marker(loc).addTo(map).on('click', 
      function(e){
        var clickedMarker = e.target;
        c_id = clickedMarker.myJsonData.clientId
        var checked = document.getElementById(c_id).checked; 
        if (checked) {
          document.getElementById(c_id).checked = false;
          clickedMarker.setIcon(blueIcon);
        }
        else {
          document.getElementById(c_id).checked = true;
          clickedMarker.setIcon(greenIcon);
        }
        toggleSubmit();
      }
  );
  marker.myJsonData = {clientId: id};
}