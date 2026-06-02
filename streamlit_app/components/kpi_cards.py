# KPI cards shown at the top of the statistics view.

import streamlit as st
import duckdb
import pandas as pd
from utils.helpers import format_sek, format_antal


def render_kpis(df: pd.DataFrame) -> None:
    """
    Render four KPI cards at the top of the statistics view.
    Takes the merged DataFrame from load_all() in helpers.py.
    """
    if df.empty:
        st.info("Inga bostäder att visa KPI:er för.")
        return

    # ── DuckDB aggregations ───────────────────────────────────────────────────
    antal        = len(df)
    snittpris    = duckdb.sql("SELECT ROUND(AVG(pris), -3)::BIGINT FROM df").fetchone()[0]
    snitt_kvm    = duckdb.sql("SELECT ROUND(AVG(boyta), 0)::INT   FROM df").fetchone()[0]
    tillgangliga = duckdb.sql("SELECT COUNT(*) FROM df WHERE tillgänglig = true").fetchone()[0]

    # ── Render ────────────────────────────────────────────────────────────────
    cols = st.columns(4)
    metrics = [
        ("Antal bostäder", format_antal(antal),     None),
        ("Snittpris",      format_sek(snittpris),   None),
        ("Snitt boyta",    f"{snitt_kvm} m²",       None),
        ("Tillgängliga",   format_antal(tillgangliga), None),
    ]
    for col, (label, value, delta) in zip(cols, metrics):
        with col:
            st.metric(label=label, value=value, delta=delta)