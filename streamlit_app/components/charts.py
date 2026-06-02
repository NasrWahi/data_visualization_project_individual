# Chart components

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import duckdb
import pandas as pd
from utils.constants import COLOR_CORAL, COLOR_SAND, COLOR_BROWN, COLOR_MUTED


# ── Helper ──────────────────────────────────────────────────────────────

def _tom_df(meddelande: str) -> None:
    st.info(meddelande)


# ── Map view charts ───────────────────────────────────────────────────────────

def render_prisdiagram(df: pd.DataFrame) -> None:
    """Bar chart: average price per area (top 15)."""
    st.markdown("#### Snittpris per område")

    pris_df = duckdb.sql("""
        SELECT
            område,
            ROUND(AVG(pris), -3)::BIGINT AS snittpris
        FROM df
        WHERE pris IS NOT NULL AND område IS NOT NULL
        GROUP BY område
        ORDER BY snittpris DESC
        LIMIT 15
    """).df()

    if pris_df.empty:
        return _tom_df("Ingen prisdata att visa.")

    fig = px.bar(
        pris_df,
        x="snittpris",
        y="område",
        orientation="h",
        color_discrete_sequence=["#93CEDE"],
        text_auto=".2s",
        labels={"snittpris": "Snittpris (kr)", "område": ""},
    )
    fig.update_layout(
        height=380,
        margin=dict(l=0, r=10, t=0, b=0),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


# ── Statistics charts ──────────────────────────────────────────────────────────

def render_snittpris_per_typ(df: pd.DataFrame) -> None:
    """Bar chart: average price by listing type."""
    st.markdown("#### Snittpris per bostadstyp")

    typ_df = duckdb.sql("""
        SELECT
            typ,
            ROUND(AVG(pris), -3)::BIGINT AS snittpris
        FROM df
        WHERE pris IS NOT NULL AND typ IS NOT NULL
        GROUP BY typ
        ORDER BY snittpris DESC
    """).df()

    if typ_df.empty:
        return _tom_df("Ingen data per bostadstyp.")

    fig = px.bar(
        typ_df,
        x="typ",
        y="snittpris",
        text_auto=".2s",
        color="typ",
        color_discrete_sequence=["#93CEDE", "#F9A890", "#FDD2B1", "#D4C8B7"],
        labels={"typ": "Bostadstyp", "snittpris": "Snittpris (kr)"},
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_upplatelseform(df: pd.DataFrame) -> None:
    """Donut chart: distribution of tenure types."""
    st.markdown("#### Fördelning upplåtelseform")

    uppl_df = duckdb.sql("""
        SELECT upplåtelseform, COUNT(*) AS antal
        FROM df
        WHERE upplåtelseform IS NOT NULL
        GROUP BY upplåtelseform
        ORDER BY antal DESC
    """).df()

    if uppl_df.empty:
        return _tom_df("Ingen data om upplåtelseform.")

    fig = px.pie(
        uppl_df,
        names="upplåtelseform",
        values="antal",
        color_discrete_sequence=["#93CEDE", "#F9A890", "#FDD2B1", "#D4C8B7"],
        hole=0.4,
    )
    fig.update_layout(
        margin=dict(t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_pris_per_kvm(df: pd.DataFrame) -> None:
    """Line chart: average price per sqm for top 15 areas."""
    st.markdown("#### Snittpris per kvm — topp 15 områden")

    kvm_df = duckdb.sql("""
        SELECT
            område,
            ROUND(AVG(pris_per_kvm), 0)::INT AS snitt_kvm_pris
        FROM df
        WHERE pris_per_kvm IS NOT NULL AND område IS NOT NULL
        GROUP BY område
        ORDER BY snitt_kvm_pris DESC
        LIMIT 15
    """).df()

    if kvm_df.empty:
        return _tom_df("Ingen pris/kvm-data att visa.")

    fig = px.line(
        kvm_df,
        x="område",
        y="snitt_kvm_pris",
        markers=True,
        color_discrete_sequence=["#93CEDE"],
        labels={"område": "Område", "snitt_kvm_pris": "Pris/kvm (kr)"},
    )
    fig.update_layout(
        xaxis_tickangle=-40,
        height=350,
        margin=dict(t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=8))
    st.plotly_chart(fig, use_container_width=True)


def render_rumsfordelning(df: pd.DataFrame) -> None:
    """Bar chart: listing count by number of rooms."""
    st.markdown("#### Antal bostäder per rumsantal")

    rum_df = duckdb.sql("""
        SELECT rum::INT AS rum, COUNT(*) AS antal
        FROM df
        WHERE rum IS NOT NULL
        GROUP BY rum
        ORDER BY rum
    """).df()

    if rum_df.empty:
        return _tom_df("Ingen rumsdata att visa.")

    fig = px.bar(
        rum_df,
        x="rum",
        y="antal",
        text_auto=True,
        color_discrete_sequence=["#93CEDE"],
        labels={"rum": "Antal rum", "antal": "Antal bostäder"},
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_snittpris_per_stad(df: pd.DataFrame) -> None:
    """Bar chart: average price by city."""
    st.markdown("#### Snittpris per stad")

    stad_df = duckdb.sql("""
        SELECT
            stad,
            ROUND(AVG(pris), -3)::BIGINT AS snittpris,
            COUNT(*) AS antal
        FROM df
        WHERE pris IS NOT NULL AND stad IS NOT NULL
        GROUP BY stad
        ORDER BY snittpris DESC
    """).df()

    if stad_df.empty:
        return _tom_df("Ingen stadsdata att visa.")

    fig = px.bar(
        stad_df,
        x="stad",
        y="snittpris",
        text_auto=".2s",
        color_discrete_sequence=["#93CEDE"],
        labels={"stad": "Stad", "snittpris": "Snittpris (kr)"},
        hover_data={"antal": True},
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_visningar_per_dag(visningar: pd.DataFrame) -> None:
    """Bar chart: number of viewings per date."""
    st.markdown("#### Visningar per dag")

    vis_df = duckdb.sql("""
        SELECT
            visningsdatum AS datum,
            COUNT(*) AS antal_visningar
        FROM visningar
        WHERE visningsdatum IS NOT NULL
        GROUP BY visningsdatum
        ORDER BY visningsdatum
    """).df()

    if vis_df.empty:
        return _tom_df("Ingen visningsdata att visa.")

    fig = px.bar(
        vis_df,
        x="datum",
        y="antal_visningar",
        color_discrete_sequence=["#93CEDE"],
        labels={"datum": "Datum", "antal_visningar": "Antal visningar"},
        text_auto=True,
    )
    fig.update_layout(
        height=350,
        margin=dict(t=0, b=0),
        xaxis_tickangle=-40,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)