# ── vyer/statistik_vy.py ─────────────────────────────────────────────────────
import streamlit as st
from utils.helpers          import load_visningar, read_css
from utils.constants        import STYLES_PATH
from components.kpi_cards   import render_kpis
from components.filter_bar  import render_filter_bar
from components.charts      import (
    render_prisdiagram,
    render_snittpris_per_typ,
    render_upplatelseform,
    render_pris_per_kvm,
    render_rumsfordelning,
    render_visningar_per_dag,
    render_snittpris_per_stad,
)


def show() -> None:
    """Renderar statistiksidan, anropas från app.py."""
    read_css(STYLES_PATH / "app.css")

    st.markdown("## Statistik")
    st.markdown("Översikt över bostadsmarknaden baserat på insamlad data.")

    # ── Sökfält + filter överst ───────────────────────────────────────────────
    df, valt_omrade = render_filter_bar()

    visningar = load_visningar()

    if df.empty:
        st.warning("Ingen data hittades. Kontrollera CSV-filerna.")
        return

    st.markdown("---")

    # ── KPI-kort ──────────────────────────────────────────────────────────────
    render_kpis(df)
    st.markdown("---")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["Priser", "Bostäder", "Visningar"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            render_prisdiagram(df)
        with col2:
            render_pris_per_kvm(df)

        col3, col4 = st.columns(2)
        with col3:
            render_snittpris_per_typ(df)
        with col4:
            render_snittpris_per_stad(df)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            render_rumsfordelning(df)
        with col2:
            render_upplatelseform(df)

    with tab3:
        if visningar.empty:
            st.info("Ingen visningsdata tillgänglig.")
        else:
            render_visningar_per_dag(visningar)