# Home view: start page with login and background image.

import base64
import streamlit as st
from utils.constants import IMAGES_DIR, CSS_HOME
from utils.helpers import logga_in, is_inloggad, read_textfile


def _get_base64_image(image_path) -> str:
    """Read an image and return it as a base64-encoded string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def show():
    """Render the home view. Called from app.py."""
    bg_path = IMAGES_DIR / "entry_vy.png"
    b64     = _get_base64_image(bg_path) if bg_path.exists() else ""

    # Load CSS template and inject the base64 background image
    css = read_textfile(CSS_HOME).replace("__BG_IMAGE__", f"data:image/png;base64,{b64}")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        st.title("Hitta rätt bostad. Enklare.")
        st.write("UTFORSKA BOSTÄDER, PRISER OCH OMRÅDEN")
        st.markdown("<br>", unsafe_allow_html=True)

        if is_inloggad():
            if st.button("Utforska bostäder ->", use_container_width=True, type="primary"):
                st.session_state["sida"] = "karta"
                st.rerun()
        else:
            with st.container(border=True):
                st.markdown("#### Logga in")
                namn = st.text_input("Ditt namn", placeholder="Skriv ditt namn...")
                if st.button("Logga in", use_container_width=True, type="primary"):
                    if namn.strip():
                        logga_in(namn)
                        st.session_state["sida"] = "karta"
                        st.rerun()
                    else:
                        st.warning("Ange ett namn för att logga in.")
                st.markdown("---")
                if st.button("Fortsätt utan konto", use_container_width=True):
                    logga_in("Gäst")
                    st.session_state["sida"] = "karta"
                    st.rerun()