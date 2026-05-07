# ── components/filter_bar.py ──────────────────────────────────────────────────
import streamlit as st
from utils.helpers import load_all, get_omraden


def render_filter_bar() -> tuple:
    """
    Renderar sökfält och filteralternativ — alltid synliga.
    Sparar filtrerat DataFrame i st.session_state["filtrerat_df"]
    så att statistiksidan kan läsa samma filter.

    Returns:
        tuple: (filtrerat DataFrame, valt område som sträng)
    """
    df      = load_all()
    omraden = get_omraden(df)

    # ── Sök-rad ───────────────────────────────────────────────────────────────
    col_sok, col_knapp = st.columns([5, 0.8])

    with col_sok:
        valt_omrade = st.selectbox(
            label="Sök område",
            options=["Alla"] + omraden,
            label_visibility="collapsed",
            key="filter_omrade",
        )
    with col_knapp:
        st.button("Sök", use_container_width=True, type="primary", key="btn_sok")

    # ── Filter alltid synligt ─────────────────────────────────────────────────
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            upplatelse = st.multiselect(
                "Upplåtelseform",
                options=["hyra", "köpa"],
                key="filter_upplatelse",
            )

        with c2:
            valda_typer = st.multiselect(
                "Bostadstyp",
                options=sorted(df["typ"].dropna().unique().tolist()),
                key="filter_typ",
            )

        with c3:
            if "hyra" in upplatelse and "köpa" not in upplatelse:
                pris_min     = 4_500
                pris_max_val = 30_000
                pris_step    = 500
            elif "köpa" in upplatelse and "hyra" not in upplatelse:
                pris_min     = 800_000
                pris_max_val = 15_000_000
                pris_step    = 100_000
            else:
                pris_min     = 4_500
                pris_max_val = 15_000_000
                pris_step    = 100_000

            pris_max = st.slider(
                "Max pris (kr)",
                min_value=pris_min,
                max_value=pris_max_val,
                value=pris_max_val,
                step=pris_step,
                key="filter_pris",
            )

        with c4:
            rum_min = st.selectbox(
                "Minst antal rum",
                options=[1, 2, 3, 4, 5, 6],
                key="filter_rum",
            )

    # ── Filtrera DataFrame ────────────────────────────────────────────────────
    if upplatelse:
        df = df[df["upplåtelseform"].isin(upplatelse)]

    if valda_typer:
        df = df[df["typ"].isin(valda_typer)]

    df = df[df["pris"] <= pris_max]
    df = df[df["rum"] >= rum_min]

    if valt_omrade != "Alla":
        df = df[df["område"] == valt_omrade]

    # ── Spara i session_state så statistik-sidan kan läsa filtret ─────────────
    st.session_state["filtrerat_df"] = df

    return df, valt_omrade