// Google Maps view logic for RightHome.
// The variables BOSTADER, AKTIVA_INIT and POI_CONFIG -> from Python
// before this script runs.

var selectedCategoryType = 'library';
var map, infoWindow, placesService, directionsService, directionsRenderer;
var bostadMarkers = [];
var placeMarkers = {};
var selectedBostad = null;
var selectedPOI = null;
var activePOI = new Set(AKTIVA_INIT);

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 59.3293, lng: 18.0686 },
        zoom: 12,
        streetViewControl: false,
        mapTypeControl: false,
        fullscreenControl: false,
        styles: [{
            featureType: "poi",
            elementType: "labels",
            stylers: [{ visibility: "off" }]
        }]
    });

    infoWindow = new google.maps.InfoWindow({ maxWidth: 280 });
    placesService = new google.maps.places.PlacesService(map);
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        suppressMarkers: true,
        polylineOptions: { strokeWeight: 4, strokeOpacity: 0.8 }
    });
    directionsRenderer.setMap(map);

    selectedBostad = null;
    selectedPOI = null;

    addBostadMarkers();

    if (BOSTADER.length > 0) {
        var bounds = new google.maps.LatLngBounds();
        BOSTADER.forEach(function(b) {
            bounds.extend({ lat: b.lat, lng: b.lng });
        });
        map.fitBounds(bounds);
    }

    AKTIVA_INIT.forEach(function(typ) {
        var btn = document.querySelector('.poi-btn[data-typ="' + typ + '"]');
        if (btn) setBtnActive(btn, true);
    });

    if (AKTIVA_INIT.length > 0) {
        google.maps.event.addListenerOnce(map, 'idle', function() {
            AKTIVA_INIT.forEach(function(typ) { showPOI(typ); });
        });
    }
}

function setBtnActive(btn, on) {
    var color = btn.getAttribute('data-color');
    btn.style.border = on ? '2.5px solid ' + color : '2.5px solid #E8D5BB';
    btn.style.background = on ? '#F5F9FF' : 'white';
    btn.style.boxShadow = on ? '0 0 0 3px ' + color + '44' : 'none';
}

function togglePOI(btn, typ) {
    selectedCategoryType = typ;

    if (activePOI.has(typ)) {
        activePOI.delete(typ);
        setBtnActive(btn, false);

        if (placeMarkers[typ]) {
            placeMarkers[typ].forEach(function(m) { m.setMap(null); });
            delete placeMarkers[typ];
        }

        //  If no POI categories are active, clear the route
        if (activePOI.size === 0) {
            if (directionsRenderer) {
                directionsRenderer.setMap(null);
                directionsRenderer.setDirections({ routes: [] });
            }
            if (infoWindow) infoWindow.close();
            selectedPOI = null;
            var clearBtn = document.getElementById("clearRoute");
            if (clearBtn) clearBtn.style.display = "none";
        }
    } else {
        activePOI.add(typ);
        setBtnActive(btn, true);
        showPOI(typ);

        if (selectedBostad) {
            triggerBostadUpdate();
        }
    }
}

function triggerBostadUpdate() {
    // Find the marker for selected 'bostad', trigger its click handler
    bostadMarkers.forEach(function(m) {
        if (m.getPosition().lat() === selectedBostad.lat &&
            m.getPosition().lng() === selectedBostad.lng) {
            google.maps.event.trigger(m, 'click');
        }
    });
}

function addBostadMarkers() {
    bostadMarkers.forEach(function(m) { m.setMap(null); });
    bostadMarkers = [];

    BOSTADER.forEach(function(b) {
        var marker = new google.maps.Marker({
            position: { lat: b.lat, lng: b.lng },
            map: map,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 7,
                fillColor: "#E8735A",
                fillOpacity: 0.9,
                strokeColor: "#fff",
                strokeWeight: 2
            }
        });

        marker.addListener("click", function() {
            selectedBostad = { lat: b.lat, lng: b.lng };

            // No POI selected, therefore show simple popup
            if (activePOI.size === 0) {
                infoWindow.setContent(buildPopup(b));
                infoWindow.open(map, marker);
                return;
            }

            var req = {
                location: selectedBostad,
                rankBy: google.maps.places.RankBy.DISTANCE,
                type: selectedCategoryType
            };

            placesService.nearbySearch(req, function(results, status) {
                if (status === "OK" && results.length > 0) {
                    var nearest = results[0];
                    selectedPOI = nearest.geometry.location;
                    infoWindow.setContent(buildPowerBIPopup(b, nearest.name));
                    infoWindow.open(map, marker);
                    showRoute(1);
                } else {
                    infoWindow.setContent(buildPopup(b));
                    infoWindow.open(map, marker);
                }
            });
        });

        bostadMarkers.push(marker);
    });
}

// Transport mode buttons in popup. Numeric mode avoids quote-escaping issues in HTML.
function transportButtons() {
    return '<div style="margin-top:10px;border-top:1px solid #eee;padding-top:10px;">'
        + '<div style="font-size:11px;color:#999;margin-bottom:6px;">Visa väg:</div>'
        + '<div style="display:flex;gap:6px;">'
        + '<button onclick="showRoute(1)" style="flex:1;padding:6px 4px;border:1px solid #E8D5BB;border-radius:8px;background:white;cursor:pointer;font-size:16px;">🚶</button>'
        + '<button onclick="showRoute(2)" style="flex:1;padding:6px 4px;border:1px solid #E8D5BB;border-radius:8px;background:white;cursor:pointer;font-size:16px;">🚌</button>'
        + '<button onclick="showRoute(3)" style="flex:1;padding:6px 4px;border:1px solid #E8D5BB;border-radius:8px;background:white;cursor:pointer;font-size:16px;">🚗</button>'
        + '</div></div>';
}

function buildPopup(b) {
    return '<div style="font-family:sans-serif;width:250px;padding:12px 14px">'
        + '<div style="font-size:15px;font-weight:700;color:#1a1a1a">' + b.adress + '</div>'
        + '<div style="font-size:11px;color:#999;margin-bottom:8px">' + b.område + '</div>'
        + '<div style="font-size:18px;font-weight:700;color:#E8735A">' + b.pris.toLocaleString('sv-SE') + ' kr</div>'
        + (b.avgift ? '<div style="font-size:11px;color:#bbb">Avgift: ' + b.avgift.toLocaleString('sv-SE') + ' kr/mån</div>' : '')
        + '<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px">'
        + '<span style="background:#f0ece8;padding:3px 10px;border-radius:20px;font-size:12px">' + b.rum + ' rum</span>'
        + '<span style="background:#f0ece8;padding:3px 10px;border-radius:20px;font-size:12px">' + b.boyta + ' kvm</span>'
        + '<span style="background:#f0ece8;padding:3px 10px;border-radius:20px;font-size:12px">' + b.typ + '</span>'
        + '</div>'
        + (selectedPOI ? transportButtons() : '<div style="font-size:11px;color:#bbb;margin-top:8px;">Klicka på en POI-markör för att visa väg.</div>')
        + '</div>';
}

function buildPOIPopup(place, cfg) {
    return '<div style="font-family:sans-serif;padding:10px 12px;min-width:180px">'
        + '<strong style="font-size:14px">' + place.name + '</strong><br>'
        + '<span style="color:#888;font-size:12px">' + (place.vicinity || '') + '</span><br>'
        + '<span style="color:' + cfg.color + ';font-size:12px;font-weight:600">' + cfg.name + '</span>'
        + (selectedBostad ? transportButtons() : '<div style="font-size:11px;color:#bbb;margin-top:8px;">Klicka på en bostad för att visa väg.</div>')
        + '</div>';
}

function buildPowerBIPopup(b, nearestName) {
    var category = "plats";
    if (POI_CONFIG[selectedCategoryType]) {
        category = POI_CONFIG[selectedCategoryType].name;
    }

    var html = '<div style="font-family:sans-serif;width:240px;padding:10px;">';
    html += '<div style="font-weight:700;font-size:16px;">' + b.pris.toLocaleString("sv-SE") + ' kr</div>';
    html += '<div style="color:#666;font-size:12px;margin-bottom:10px;">' + b.adress + '</div>';
    html += '<div style="border-top:1px solid #eee;padding-top:10px;margin-top:10px;">';
    html += '<div style="font-size:10px;color:#E8735A;font-weight:bold;text-transform:uppercase;">Närmaste ' + category + '</div>';
    html += '<div style="font-size:13px;margin:5px 0;font-weight:600;">' + nearestName + '</div>';
    html += transportButtons();
    html += '</div></div>';
    return html;
}

function showRoute(val) {
    if (!selectedBostad || !selectedPOI) return;

    var mode = "WALKING";
    if (val === 2) mode = "TRANSIT";
    if (val === 3) mode = "DRIVING";
    if (typeof val === "string") mode = val;

    // Clears old renderer before creating a new one
    if (directionsRenderer) {
        directionsRenderer.setMap(null);
        directionsRenderer.setDirections({ routes: [] });
    }

    directionsRenderer = new google.maps.DirectionsRenderer({
        suppressMarkers: true,
        polylineOptions: {
            strokeColor: '#E8735A',
            strokeWeight: 5,
            strokeOpacity: 0.8
        }
    });
    directionsRenderer.setMap(map);

    directionsService.route({
        origin: selectedBostad,
        destination: selectedPOI,
        travelMode: google.maps.TravelMode[mode]
    }, function(result, status) {
        if (status === 'OK') {
            directionsRenderer.setDirections(result);
            var btn = document.getElementById("clearRoute");
            if (btn) btn.style.display = "block";
        }
    });
}

function clearRoute() {
    // Hide the route line
    if (directionsRenderer) {
        directionsRenderer.setDirections({ routes: [] });
        directionsRenderer.setMap(null);
    }

    // Create a fresh empty renderer for next
    directionsRenderer = new google.maps.DirectionsRenderer({
        suppressMarkers: true,
        map: map,
        polylineOptions: { strokeColor: '#E8735A', strokeWeight: 5 }
    });

    // Close popup
    if (infoWindow) infoWindow.close();

    // Remove all POI markers
    if (placeMarkers) {
        Object.keys(placeMarkers).forEach(function(typ) {
            placeMarkers[typ].forEach(function(m) { m.setMap(null); });
            placeMarkers[typ] = [];
        });
    }

    // Reset state
    selectedBostad = null;
    selectedPOI = null;

    // Hide the clear button
    var btn = document.getElementById("clearRoute");
    if (btn) btn.style.display = "none";
}

function showPOI(type) {
    var cfg = POI_CONFIG[type];
    if (!cfg) return;

    // Clear any existing markers for this type first
    if (placeMarkers[type]) {
        placeMarkers[type].forEach(function(m) { m.setMap(null); });
    }
    placeMarkers[type] = [];

    var bounds = map.getBounds();
    var center = bounds ? bounds.getCenter() : map.getCenter();

    placesService.nearbySearch({
        location: center,
        radius: 2000,
        type: type
    }, function(results, status) {
        if (status === "OK") {
            results.forEach(function(place) {
                var m = new google.maps.Marker({
                    position: place.geometry.location,
                    map: map,
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 4,
                        fillColor: cfg.color,
                        fillOpacity: 0.7,
                        strokeWeight: 1
                    }
                });
                placeMarkers[type].push(m);
            });
        }
    });
}

// Expose globally, so HTML onclick handlers can find them
window.initMap = initMap;
window.clearRoute = clearRoute;
window.showRoute = showRoute;
window.togglePOI = togglePOI;