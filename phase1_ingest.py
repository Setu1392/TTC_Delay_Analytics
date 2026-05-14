"""
=============================================================
TTC Transit Delay Analytics Pipeline
Phase 1: Data Ingestion & SQLite Database Setup
=============================================================
Author : Setu Patel
Dataset : TTC Bus & Subway Delay Data (Toronto Open Data)
Source  : https://open.toronto.ca/dataset/ttc-bus-delay-data/
          https://open.toronto.ca/dataset/ttc-subway-delay-data/
=============================================================
"""

import os
import sqlite3
import requests
import pandas as pd

# ── Config ─────────────────────────────────────────────────
DB_PATH   = "ttc_delays.db"
DATA_DIR  = "data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

PACKAGES = {
    "bus":    "ttc-bus-delay-data",
    "subway": "ttc-subway-delay-data",
}

CKAN_BASE = "https://ckan0.cf.opendata.inter.prod-toronto.ca"


# ── Step 1: Download CSVs from Toronto Open Data ───────────
def fetch_resource_list(package_id):
    url = f"{CKAN_BASE}/api/3/action/package_show"
    resp = requests.get(url, params={"id": package_id}, timeout=30)
    resp.raise_for_status()
    return resp.json()["result"]["resources"]


def download_csvs(package_id, label, max_files=6):
    resources = fetch_resource_list(package_id)
    csv_resources = [r for r in resources if r["format"].upper() == "CSV"]
    csv_resources = sorted(csv_resources, key=lambda r: r["name"], reverse=True)
    csv_resources = csv_resources[:max_files]

    paths = []
    for resource in csv_resources:
        filename = f"{label}_{resource['name'].replace(' ', '_')}.csv"
        filepath = os.path.join(DATA_DIR, filename)

        if os.path.exists(filepath):
            print(f"  [cached]   {filename}")
        else:
            print(f"  [download] {filename} ...")
            r = requests.get(resource["url"], timeout=60)
            r.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(r.content)

        paths.append(filepath)

    return paths


# ── Step 2: Load & Normalise CSVs ──────────────────────────
BUS_COLS = {
    "Date":      "date",
    "Route":     "route",
    "Time":      "time",
    "Day":       "day_of_week",
    "Location":  "location",
    "Incident":  "incident",
    "Min Delay": "delay_minutes",
    "Min Gap":   "gap_minutes",
    "Direction": "direction",
    "Vehicle":   "vehicle_id",
}

SUBWAY_COLS = {
    "Date":      "date",
    "Time":      "time",
    "Day":       "day_of_week",
    "Station":   "station",
    "Code":      "code",
    "Min Delay": "delay_minutes",
    "Min Gap":   "gap_minutes",
    "Bound":     "direction",
    "Line":      "line",
    "Vehicle":   "vehicle_id",
}


def load_bus_files(paths):
    frames = []
    for p in paths:
        if "code_description" in p.lower() or "code description" in p.lower():
            print(f"  [skip] {os.path.basename(p)} (lookup table)")
            continue
        try:
            df = pd.read_csv(p, dtype=str)
            df = df.rename(columns={c: BUS_COLS[c] for c in BUS_COLS if c in df.columns})
            df = df.loc[:, ~df.columns.duplicated()]
            frames.append(df)
        except Exception as e:
            print(f"  [warn] skipping {p}: {e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def load_subway_files(paths):
    frames = []
    for p in paths:
        if "code_description" in p.lower() or "code description" in p.lower():
            print(f"  [skip] {os.path.basename(p)} (lookup table)")
            continue
        try:
            df = pd.read_csv(p, dtype=str)
            df = df.rename(columns={c: SUBWAY_COLS[c] for c in SUBWAY_COLS if c in df.columns})
            df = df.loc[:, ~df.columns.duplicated()]
            frames.append(df)
        except Exception as e:
            print(f"  [warn] skipping {p}: {e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def clean_common(df):
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in ["delay_minutes", "gap_minutes"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["date", "delay_minutes"])
    df = df[df["delay_minutes"] >= 0]

    df["year"]        = df["date"].dt.year
    df["month"]       = df["date"].dt.month
    df["hour"]        = pd.to_datetime(df["time"], format="%H:%M", errors="coerce").dt.hour
    df["day_of_week"] = df["date"].dt.day_name()

    return df.reset_index(drop=True)


# ── Step 3: Write to SQLite ────────────────────────────────
def write_to_sqlite(bus_df, subway_df, db_path):
    conn = sqlite3.connect(db_path)

    if not bus_df.empty:
        bus_df.to_sql("bus_delays", conn, if_exists="replace", index=False)
        print(f"  [db] bus_delays      → {len(bus_df):,} rows")

    if not subway_df.empty:
        subway_df.to_sql("subway_delays", conn, if_exists="replace", index=False)
        print(f"  [db] subway_delays   → {len(subway_df):,} rows")

    # Create indexes individually — skip gracefully if column doesn't exist
    indexes = [
        ("idx_bus_date",  "bus_delays",    "date"),
        ("idx_bus_route", "bus_delays",    "route"),
        ("idx_sub_date",  "subway_delays", "date"),
        ("idx_sub_line",  "subway_delays", "line"),
    ]
    with conn:
        for idx_name, table, col in indexes:
            try:
                conn.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({col})")
            except sqlite3.OperationalError as e:
                print(f"  [index skip] {idx_name}: {e}")

    conn.close()
    print(f"\n  [db] saved → {db_path}")


# ── Step 4: Quick Validation Queries ──────────────────────
def validate_db(db_path):
    conn = sqlite3.connect(db_path)
    print("\n── Validation ─────────────────────────────────────────")

    for table in ["bus_delays", "subway_delays"]:
        try:
            row_count = pd.read_sql(f"SELECT COUNT(*) AS cnt FROM {table}", conn).iloc[0, 0]
            date_range = pd.read_sql(
                f"SELECT MIN(date) AS earliest, MAX(date) AS latest FROM {table}", conn
            )
            print(f"\n  {table}")
            print(f"    Rows       : {row_count:,}")
            print(f"    Date range : {date_range['earliest'][0]}  →  {date_range['latest'][0]}")

            cause_col = "incident" if table == "bus_delays" else "code"
            top_delays = pd.read_sql(
                f"""
                SELECT {cause_col} AS cause,
                       COUNT(*) AS incidents,
                       ROUND(AVG(delay_minutes), 1) AS avg_delay_min
                FROM   {table}
                GROUP  BY 1
                ORDER  BY incidents DESC
                LIMIT  5
                """,
                conn,
            )
            print(f"\n    Top 5 delay causes:\n{top_delays.to_string(index=False)}")
        except Exception as e:
            print(f"  [warn] {table}: {e}")

    conn.close()


# ── Main ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  TTC Delay Analytics — Phase 1: Ingestion")
    print("=" * 60)

    print("\n[1/4] Downloading bus delay CSVs ...")
    bus_paths = download_csvs(PACKAGES["bus"], "bus")

    print("\n[2/4] Downloading subway delay CSVs ...")
    subway_paths = download_csvs(PACKAGES["subway"], "subway")

    print("\n[3/4] Loading and cleaning data ...")
    bus_df    = clean_common(load_bus_files(bus_paths))
    subway_df = clean_common(load_subway_files(subway_paths))
    print(f"  Bus rows    : {len(bus_df):,}")
    print(f"  Subway rows : {len(subway_df):,}")

    print("\n[4/4] Writing to SQLite ...")
    write_to_sqlite(bus_df, subway_df, DB_PATH)

    validate_db(DB_PATH)

    print("\n✅ Phase 1 complete. Run phase2_eda.py next.\n")
