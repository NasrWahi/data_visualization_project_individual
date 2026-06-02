# Helper functions used across the app.
# Imported by components and views: from utils.helpers import

import pandas as pd
import streamlit as st
from pathlib import Path
from utils.constants import (
    CSV_BOSTADER, CSV_PRISER, CSV_PLATSER, CSV_VISNINGAR,
    COL_ID, COL_BOSTAD_ID, COL_PLATS_ID,
    COL_PRIS, COL_KVM, COL_PRIS_PER_KVM,
    COL_OMRADE, COL_KOMMUN_BEFOLKNING,
    ETL_DIR,
)

# ── File reading ──────────────────────────────────────────────────────────────

def read_textfile(path: Path) -> str:
    """Read a text file and return its contents as a string."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_css(path: Path) -> None:
    """Load a CSS file and inject it into Streamlit via st.markdown."""
    css = read_textfile(path)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ── Data loading ──────────────────────────────────────────────────────────────

# For issues in Streamlit
# Conversions, DuckDB reads all DF
def _cast_strings_to_object(df: pd.DataFrame) -> pd.DataFrame:
    """Convert pyarrow string columns to object, so that the DuckDB can read them."""
    for col in df.select_dtypes(include="string").columns:
        df[col] = df[col].astype("object")
    return df


@st.cache_data
def load_bostader() -> pd.DataFrame:
    """Load bostader.csv."""
    return _cast_strings_to_object(pd.read_csv(CSV_BOSTADER))


@st.cache_data
def load_priser() -> pd.DataFrame:
    """Load priser.csv."""
    return _cast_strings_to_object(pd.read_csv(CSV_PRISER))


@st.cache_data
def load_platser() -> pd.DataFrame:
    """Load platser.csv."""
    return _cast_strings_to_object(pd.read_csv(CSV_PLATSER))


@st.cache_data
def load_visningar() -> pd.DataFrame:
    """Load visningar.csv."""
    return _cast_strings_to_object(pd.read_csv(CSV_VISNINGAR))


@st.cache_data
def load_all() -> pd.DataFrame:
    """
    Load and merge all CSV files into a single DataFrame.
    bostader <- priser  (joined on bostad_id)
    bostader <- platser (joined on plats_id)
    """
    bostader = load_bostader()
    priser   = load_priser()
    platser  = load_platser()

    df = bostader.merge(
        priser,
        left_on=COL_ID,
        right_on=COL_BOSTAD_ID,
        how="left",
        suffixes=("", "_pris"),
    )

    df = df.merge(
        platser,
        on=COL_PLATS_ID,
        how="left",
        suffixes=("", "_plats"),
    )

    return df


# ── Formatting ────────────────────────────────────────────────────────────────

def format_sek(val) -> str:
    """Format a number as SEK. Example: 4372299 -> '4.4M kr'."""
    try:
        v = int(val)
        if v >= 1_000_000:
            return f"{v/1_000_000:.1f}M kr"
        elif v >= 1_000:
            return f"{v/1_000:.0f}k kr"
        return f"{v:,} kr"
    except (ValueError, TypeError):
        return "—"


def format_antal(val) -> str:
    """Format a large integer with thousands separator. Example: 995574 -> '995 574'."""
    try:
        return f"{int(val):,}".replace(",", " ")
    except (ValueError, TypeError):
        return "—"


# ── Statistics ────────────────────────────────────────────────────────────────

def get_snittpris(df: pd.DataFrame) -> int:
    """Return the average price for a filtered DataFrame."""
    try:
        return int(df[COL_PRIS].mean())
    except (ValueError, TypeError, KeyError):
        return 0


def get_snittpris_per_kvm(df: pd.DataFrame) -> int:
    """Return the average price per square meter."""
    try:
        return int(df[COL_PRIS_PER_KVM].mean())
    except (ValueError, TypeError, KeyError):
        return 0


def get_befolkning(df: pd.DataFrame) -> int:
    """Return the total population for the filtered areas."""
    try:
        return int(df[COL_KOMMUN_BEFOLKNING].sum())
    except (ValueError, TypeError, KeyError):
        return 0


def get_omraden(df: pd.DataFrame) -> list:
    """Return a sorted list of unique areas."""
    try:
        return sorted(df[COL_OMRADE].dropna().unique().tolist())
    except (ValueError, TypeError, KeyError):
        return []


def get_snittpris_per_omrade(df: pd.DataFrame) -> pd.DataFrame:
    """Return average price grouped by area, sorted descending."""
    try:
        return (
            df.groupby(COL_OMRADE)[COL_PRIS]
            .mean()
            .sort_values(ascending=False)
            .head(20)
            .reset_index()
            .rename(columns={COL_OMRADE: "Område", COL_PRIS: "Snittpris"})
        )
    except (ValueError, TypeError, KeyError):
        return pd.DataFrame()


# ── Authentication ────────────────────────────────────────────────────────────

def is_inloggad() -> bool:
    """Return True if a user is logged in via session state."""
    return bool(st.session_state.get("anvandare", "").strip())


def get_anvandare() -> str:
    """Return the name of the currently logged-in user."""
    return st.session_state.get("anvandare", "")


def logga_in(namn: str) -> None:
    """Store the username in session state."""
    st.session_state["anvandare"] = namn.strip()


def logga_ut() -> None:
    """Clear the user from session state."""
    st.session_state["anvandare"] = ""


# ── Saved listings ────────────────────────────────────────────────────────────

CSV_SPARADE = ETL_DIR / "sparade.csv"


def _init_sparade_csv() -> None:
    """Create sparade.csv if it does not exist yet."""
    if not CSV_SPARADE.exists():
        pd.DataFrame(columns=["anvandare", "bostad_id"]).to_csv(CSV_SPARADE, index=False)


def load_sparade_for_user(anvandare: str) -> list:
    """Return a list of bostad_id values saved by the given user."""
    _init_sparade_csv()
    try:
        df = pd.read_csv(CSV_SPARADE)
        return df[df["anvandare"] == anvandare]["bostad_id"].tolist()
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return []


def spara_bostad(anvandare: str, bostad_id: int) -> None:
    """Save a listing for the user if not already saved."""
    _init_sparade_csv()
    df = pd.read_csv(CSV_SPARADE)
    already_saved = ((df["anvandare"] == anvandare) & (df["bostad_id"] == bostad_id)).any()
    if not already_saved:
        new_row = pd.DataFrame([{"anvandare": anvandare, "bostad_id": bostad_id}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(CSV_SPARADE, index=False)


def ta_bort_sparad(anvandare: str, bostad_id: int) -> None:
    """Remove a saved listing for the user."""
    _init_sparade_csv()
    df = pd.read_csv(CSV_SPARADE)
    df = df[~((df["anvandare"] == anvandare) & (df["bostad_id"] == bostad_id))]
    df.to_csv(CSV_SPARADE, index=False)


def is_sparad(anvandare: str, bostad_id: int) -> bool:
    """Return True if the listing is saved by the given user."""
    return bostad_id in load_sparade_for_user(anvandare)