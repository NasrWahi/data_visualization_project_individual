# Map view: renders an interactive Google Maps iframe with POI buttons
# + followed by the recommended/saved/upcoming-viewings sidebar.

import json
import base64

import streamlit as st
import streamlit.components.v1 as components

from components.filter_bar import render_filter_bar
from components.objekt_lista import render_sparade, render_visningar, render_rekommenderade
from utils.constants import (
    GOOGLE_MAPS_KEY,
    ICONS_DIR,
    POI_OPTIONS as POI_CONST,
    CSS_MAP,
    JS_MAP,
)
from utils.helpers import read_textfile

# POI marker colors
POI_COLORS = {
    "library":         "#E53935",
    "transit_station": "#00897B",
    "restaurant":      "#F57C00",
    "gym":             "#8E24AA",
    "supermarket":     "#1E88E5",
    "school":          "#43A047",
}

POI_LIST = [
    (info["icon"], namn, info["google_type"])
    for namn, info in POI_CONST.items()
]


def get_icon_b64(filename: str) -> str:
    """Return a base64-encoded icon file so it can be inlined into the iframe."""
    filepath = ICONS_DIR / filename
    if filepath.exists():
        return base64.b64encode(filepath.read_bytes()).decode()
    return ""


def _build_bostader_payload(df) -> list:
    """Convert a filtered DataFrame into the minimal dict list the JS expects."""
    bostader = []
    for _, row in df.iterrows():
        try:
            lat = float(row.get("lat", 0))
            lng = float(row.get("lon", 0))
            if lat == 0 or lng == 0:
                continue
            bostader.append({
                "lat":    lat,
                "lng":    lng,
                "adress": str(row.get("adress", "—")),
                "pris":   int(row.get("pris", 0)),
                "avgift": int(row.get("avgift", 0)),
                "rum":    int(row.get("rum", 0)),
                "boyta":  int(row.get("boyta", 0)),
                "typ":    str(row.get("typ", "—")),
                "område": str(row.get("område", "—")),
            })
        except (ValueError, TypeError):
            continue
    return bostader


def _build_poi_buttons_html() -> str:
    """Render the POI button grid as HTML using inlined base64 icons."""
    html = ""
    for icon_file, _, typ in POI_LIST:
        b64   = get_icon_b64(icon_file)
        color = POI_COLORS.get(typ, "#C97B5A")
        img_tag = (
            f'<img src="data:image/png;base64,{b64}">'
            if b64 else
            '<div class="poi-btn-placeholder"></div>'
        )
        html += (
            f'<div class="poi-btn" data-typ="{typ}" data-color="{color}" '
            f"onclick=\"togglePOI(this, '{typ}')\">"
            f"{img_tag}"
            "</div>"
        )
    return html


def build_map_html(df, api_key: str, aktiva: list) -> str:
    """Assemble the iframe HTML by injecting data into pre-built CSS and JS files."""
    bostader     = _build_bostader_payload(df)
    bostader_js  = json.dumps(bostader, ensure_ascii=False)
    aktiva_js    = json.dumps(aktiva)
    poi_config   = {
        typ: {"name": namn, "color": POI_COLORS.get(typ, "#C97B5A")}
        for _, namn, typ in POI_LIST
    }
    poi_config_js = json.dumps(poi_config)

    # Load CSS and JS from disk, in turn the Python file stays small + follows DRY principle
    css      = read_textfile(CSS_MAP)
    map_js   = read_textfile(JS_MAP)
    buttons  = _build_poi_buttons_html()

    # Variables BOSTADER, AKTIVA_INIT and POI_CONFIG are read by map.js
    injected_vars = (
        f"var BOSTADER = {bostader_js};\n"
        f"var AKTIVA_INIT = {aktiva_js};\n"
        f"var POI_CONFIG = {poi_config_js};\n"
    )

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>{css}</style>
</head>
<body>
<div id="wrapper">
  <div id="map"></div>
  <div id="poi-panel">
    <div id="poi-title">Visa närhet till</div>
    <div class="poi-grid">{buttons}</div>
  </div>
</div>
<div id="infoPanel">Laddar...</div>
<button id="clearRoute" onclick="clearRoute()">&#x2715; Rensa rutt</button>
<script>{injected_vars}{map_js}</script>
<script src="https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=places&callback=initMap" async defer></script>
</body>
</html>"""


def show():
    """Render the map view. Called from app.py."""
    if "aktiva_poi" not in st.session_state:
        st.session_state["aktiva_poi"] = []

    df_filtrerad, _ = render_filter_bar()
    st.markdown("---")

    if not GOOGLE_MAPS_KEY:
        st.warning("Lägg till GOOGLE_MAPS_API_KEY i din .env-fil!")
        return

    html = build_map_html(df_filtrerad, GOOGLE_MAPS_KEY, st.session_state["aktiva_poi"])
    components.html(html, height=650, scrolling=False)

    st.markdown("---")

    col_main, col_side = st.columns([2.5, 1], gap="large")

    with col_main:
        render_rekommenderade(df_filtrerad)

    with col_side:
        render_sparade()
        st.markdown("---")
        render_visningar()