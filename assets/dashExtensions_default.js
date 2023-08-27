window.dashExtensions = Object.assign({}, window.dashExtensions, {
    dashExtensionssub: {
        customMarker: function(feature, latlng) {
                return L.marker(latlng, {
                    icon: L.icon({
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-violet.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34],
                        shadowSize: [41, 41]
                    })
                });
            }
    }
});