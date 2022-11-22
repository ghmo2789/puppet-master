
var map = L.map('mapid').setView([30, 0], 0.5);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
              maxZoom: 19,
              attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                }).addTo(map);
var jsonData = JSON.parse(document.querySelector('#jsonData').getAttribute('data-json'));
var locations = jsonData.locations;
for (const loc of locations) {
  L.marker(loc).addTo(map);
}