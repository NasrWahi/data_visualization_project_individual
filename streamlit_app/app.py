# Main entry: page config, sidebar navigation and routing.

import streamlit as st
from utils.constants import APP_TITLE, APP_ICON, LOGO_PATH, CSS_APP
from utils.helpers import is_inloggad, get_anvandare, logga_ut, read_css
from vyer.home import show as show_home
from vyer.karta_vy import show as show_karta
from vyer.statistik_vy import show as show_statistik

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Default page on first load
if "sida" not in st.session_state:
    st.session_state["sida"] = "home"

# Global styles loaded from assets/style/app.css
read_css(CSS_APP)

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=200)
    else:
        st.title("RightHome")

    st.markdown("---")

    if is_inloggad():
        st.caption(f"Inloggad som: **{get_anvandare()}**")
        st.markdown("---")

    if st.button("Home", use_container_width=True):
        st.session_state["sida"] = "home"
        st.rerun()

    if st.button("Karta", use_container_width=True):
        st.session_state["sida"] = "karta"
        st.rerun()

    if st.button("Statistik", use_container_width=True):
        st.session_state["sida"] = "statistik"
        st.rerun()

    if is_inloggad():
        st.markdown("---")
        if st.button("Logga ut", use_container_width=True):
            logga_ut()
            st.session_state["sida"] = "home"
            st.rerun()

# ── Routing ───────────────────────────────────────────────────────────────────
if st.session_state["sida"] == "home":
    show_home()
elif st.session_state["sida"] == "karta":
    show_karta()
elif st.session_state["sida"] == "statistik":
    show_statistik()