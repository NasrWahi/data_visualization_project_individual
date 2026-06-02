# Data Visualization Project: RightHome

## Swedish Housing Market Dashboard

# Overview

This project implements an interactive housing market dashboard built with Streamlit (also Power BI), designed to help users explore Swedish real estate data across Stockholm, Malmö and Göteborg. Built in collaboration with a UX team (which helped design the user interface for Power BI) as part of a team of Data Engineers. The dashboard combines an ETL pipeline, exploratory data analysis, data storytelling and a fully functional web application with map integration, filtering and personalised user accounts.

The dataset used throughout the project is mock data generated for educational purposes, as access to live real estate APIs was unavailable due to external limitations beyond the scope of the group. The mock data can be found in the src folder (e.g., data/bostader.json).

This repository specifically is a continuation of the original group project, with the Streamlit dashboard reworked individually. The code structure was rewritten to follow the DRY principle more strictly: chart logic was consolidated into a single component module, CSS was extracted from Python files into dedicated stylesheets under `assets/style/`, and the embedded JavaScript powering the map was moved to its own file under `assets/js/`. The goal was simple: a cleaner separation of concerns and a less cluttered codebase.

The project consists of four main parts:

1. **ETL Pipeline** that ingests, transforms and loads housing data
2. **Exploratory Data Analysis** with matplotlib-based data storytelling
3. **Power BI dashboard** with KPIs, filters, what-if analysis and interactive visuals
4. **Streamlit dashboard** with KPI cards, interactive maps, statistics and user login

# Objectives

- Design and implement a complete data flow from raw data to interactive visualisation.
- Apply data engineering principles: separation of concerns, DRY code structure and reproducible pipelines.
- Use DuckDB for efficient SQL aggregations directly against pandas DataFrames.
- Apply data storytelling principles to communicate insights, not just display data.
- Deploy a production-ready Streamlit app accessible via a public URL.

# Architecture

The repository is organised so that each layer of the application has a clear, single responsibility. With a structure that follows a DRY principle, where each piece of logic lives in exactly one place, and views import what they need from `components/` and `utils/` rather than duplicating it.

# Features

## ETL Pipeline

A reproducible flow that generates a synthetic housing dataset and processes it through three stages:

1. **Extract**: Reads raw JSON files containing generated housing data, SCB demographic statistics and OpenStreetMap POI counts.
2. **Transform**: Validates schemas, joins SCB data into places, attaches POI counts to listings and filters invalid rows. Produces four clean CSVs.
3. **Load**: Optionally uploads to Supabase for cloud storage. The dashboard itself reads directly from local CSV files.

## Power BI Dashboard

The initial visualisation layer was built in Power BI as a foundation for the team's design work. It includes filters for area, listing type and price range, KPIs for average price, listing count and available units, and bar and line charts for market trends. What-if parameters let users adjust budget assumptions and immediately see the effect on affordability across cities. Coding was simitaneously done on Visual Studio Code and Power BI, with Python scripts for data transformation and DAX for measures and other calculated columns.

## Streamlit Dashboard

- **Home view**: Login form with background image and a guest option.
- **Map view**: Google Maps integration with clickable listings. Selecting a POI category (library, gym, public transport, etc.) shows the nearest match and a walking, transit or driving route from the selected listing.
- **Statistics view**: KPI cards followed by tabbed charts for prices, listings and viewings, all powered by DuckDB aggregations against pandas DataFrames.
- **Simple session-based login**: Users enter only their name to log in. Saved listings are persisted per user in `sparade.csv` and remain available between sessions.

https://righthome.streamlit.app/

## Data Storytelling

Three matplotlib charts in `notebooks/eda_nasser.ipynb` apply storytelling principles:

- **Active titles** that state an insight rather than describe a chart ("Stockholm costs nearly *double* per square metre…").
- **Visual highlighting**: Stockholm is rendered in coral while other cities are greyed out, directing the reader's attention.
- **Minimal chartjunk**: gridlines and spines are removed where they do not aid interpretation.

## Code Quality

- Separation between Python logic, CSS styling and JavaScript map code. All styling lives under `assets/style/`, all JavaScript under `assets/js/`.
- All chart logic is collected in `components/charts.py`. Views remain thin and only orchestrate layout.
- Constants such as paths, column names and colors live in `utils/constants.py`. Changing a value in one place updates the whole app.
- All comments and docstrings are written in English. User-facing strings, data values and column names remain in Swedish to match the source data.

# Installation & Usage

## Essential Requirements

- Python 3.13 or higher
- Virtual environment (`.venv`)
- A Google Maps API key with **Maps JavaScript API** and **Places API** enabled (only required for the map view)

# 1. Setup Environment

## Activate the virtual environment (Windows Git Bash):

```
source .venv/Scripts/activate
```

## Install dependencies:

```
uv pip install -e . # Installs the package in editable mode, allowing imports from streamlit_app/
```

And in case of a warning and a certificate error on e.g. Windows:
```
uv pip install -r pyproject.toml --native-tls
```

## Configure the Google Maps API key:

Create a `.env` file in the project root containing:

```
GOOGLE_MAPS_API_KEY=your_api_key_here
```

The file is already listed in `.gitignore` and will not be committed.

# 2. Execution

## Generate data and run the ETL pipeline (only needed once, or after schema changes):

```
python src/data/generate_data.py
python ETL_Pipline/transform.py
python ETL_Pipline/set_sparad.py
```

## Run the Streamlit dashboard:

```
python -m streamlit run streamlit_app/app.py
```

The dashboard opens automatically at `http://localhost:8501`.

# 3. Verification

After execution, verify the following:

- **CSV files**: confirm `bostader.csv`, `priser.csv`, `platser.csv` and `visningar.csv` exist in `ETL_Pipline/`.
- **Dashboard**: the home view should load with the login form. After logging in, all three views (Home, Karta, Statistik) should be navigable from the sidebar. Login should persist across views, and saved listings should remain available after logging out and back in again. However, logging in is not necessary, it's fully functional without any authentication.
- **Map**: with a valid API key configured, the map view should display listings as coral markers across Stockholm, Malmö and Göteborg.
