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
