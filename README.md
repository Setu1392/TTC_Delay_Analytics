# 🚌 TTC Delay Analytics Pipeline
> An end-to-end data analytics project analyzing Toronto Transit Commission delay patterns across bus and subway networks (2025–2026).

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?logo=sqlite)
![Dash](https://img.shields.io/badge/Dash-Interactive%20Dashboard-darkgreen?logo=plotly)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Wrangling-purple?logo=pandas)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-orange)

---

## 📌 Project Overview

This project builds a complete data analytics pipeline on real public transit data from the [City of Toronto Open Data Portal](https://open.toronto.ca/). It covers the full analyst workflow: ingestion, storage, cleaning, SQL-based exploration, static visualization, and an interactive dashboard.

**Dataset:** TTC Bus & Subway Delay Data — 97,500+ incident records from January 2025 to January 2026.

---

## 🔍 Key Findings

| Metric | Bus | Subway |
|--------|-----|--------|
| Total Incidents | 60,327 | 10,087 |
| Avg Delay | 23.7 min | 8.2 min |
| Total Delay Hours | 23,837 hrs | 1,385 hrs |
| Peak Hour | 5:00 PM | 6:00 AM |

### Highlights
- 🔴 **Buses experience 6x more incidents** than the subway and delays nearly 3x longer on average
- ⚠️ **Delay code MFDV** (mechanical failure / disabled vehicle) averages a staggering **127 minutes** per incident — the single most impactful cause on the bus network
- 🛣️ **29 Dufferin** is the worst bus route with 35,052 total delay minutes across the period
- 🚇 **Wilson and Kipling stations** are the highest-incident subway stations, likely due to end-of-line storage activity
- 📈 **January 2026 spike** visible in both modes — consistent with severe winter weather conditions
- 📅 **Thursdays** see the most bus incidents; **Sundays** have the longest average delays (25.8 min)

---

## 🗂️ Project Structure

```
ttc-delay-analytics/
│
├── data/
│   └── raw/                    # Downloaded CSVs (auto-created)
│
├── charts/                     # Output PNG charts (auto-created)
│   ├── 01_kpi_summary.png
│   ├── 02_delays_by_hour.png
│   ├── 03_delays_by_dow.png
│   ├── 04_monthly_trend.png
│   ├── 05_top_bus_routes.png
│   └── 06_top_subway_stations.png
│
├── phase1_ingest.py            # Data download, cleaning & SQLite ingestion
├── phase2_eda.py               # SQL-based exploratory data analysis
├── phase3_viz.py               # Static chart generation (Matplotlib)
├── phase4_dashboard.py         # Interactive Dash dashboard
├── ttc_delays.db               # SQLite database (auto-created)
└── README.md
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.10+** | Core language |
| **Pandas** | Data wrangling, cleaning, feature engineering |
| **SQLite3** | Relational database storage and querying |
| **SQL** | Exploratory analysis — aggregations, filtering, indexing |
| **Matplotlib** | Static chart generation |
| **Plotly / Dash** | Interactive dashboard |
| **Requests** | API calls to Toronto Open Data |

---

## 🚀 Setup & Usage

### 1. Clone the repository
```bash
git clone https://github.com/Setu1392/ttc-delay-analytics.git
cd ttc-delay-analytics
```

### 2. Install dependencies
```bash
pip install pandas requests matplotlib plotly dash
```

### 3. Run the pipeline in order

**Phase 1 — Ingest data into SQLite**
```bash
python phase1_ingest.py
```
Downloads TTC delay CSVs from Toronto Open Data, cleans them, and loads ~97,500 rows into a local SQLite database.

**Phase 2 — Run EDA queries**
```bash
python phase2_eda.py
```
Runs 10 SQL analyses covering delay summaries, peak hours, worst routes/stations, day-of-week patterns, and monthly trends.

**Phase 3 — Generate charts**
```bash
python phase3_viz.py
```
Produces 6 publication-ready PNG charts saved to the `charts/` folder.

**Phase 4 — Launch the dashboard**
```bash
python phase4_dashboard.py
```
Starts a local Dash app at **http://127.0.0.1:8050** with interactive filters for mode (Bus/Subway) and date range.

---

## 📊 Dashboard Features

- **Mode toggle** — switch between Bus and Subway views instantly
- **Date range slider** — filter all charts to any month range
- **4 KPI cards** — total incidents, avg delay, worst single delay, total delay hours
- **Hourly chart** — incidents by hour with peak highlighted
- **Day of week chart** — busiest days compared
- **Monthly trend** — incident volume over time with area fill
- **Top routes / stations** — worst performers by total delay or incident count
- **Worst delays table** — sortable, top 50 worst individual delays
- ![Dashboard](screenshots/Dashboard.png)

---

## 💡 Skills Demonstrated

- End-to-end data pipeline design (extract → transform → load → analyze → visualize)
- REST API data ingestion from a public open data portal
- Relational database design and indexing with SQLite
- Data cleaning and feature engineering with Pandas
- Exploratory data analysis using SQL aggregations and window patterns
- Data storytelling through static and interactive visualizations
- Dashboard development with callback-driven interactivity (Dash)

---

## 📁 Data Source

- [TTC Bus Delay Data — Toronto Open Data](https://open.toronto.ca/dataset/ttc-bus-delay-data/)
- [TTC Subway Delay Data — Toronto Open Data](https://open.toronto.ca/dataset/ttc-subway-delay-data/)

Data is downloaded programmatically via the CKAN API and is refreshed automatically on each run.

---

## 👤 Author

**Setu Patel**
M.Sc. Big Data Analytics — Trent University
[LinkedIn](https://linkedin.com/in/setu-patel-551973209) · [GitHub](https://github.com/Setu1392)
