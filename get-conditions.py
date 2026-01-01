import pandas as pd
from datetime import datetime, timezone

import json
from esridump.dumper import EsriDumper

d = EsriDumper('https://services2.arcgis.com/WLyMuW006nKOfa5Z/ArcGIS/rest/services/RCS_Status_PUBLIC/FeatureServer/0')

csv_file_path = 'current_conditions.csv'
existing_df = pd.read_csv(csv_file_path)
all_feat = list(d)

# Example data
data = all_feat
# Function to flatten the dictionary
def flatten_dict(d):
    def expand(key, value):
        if isinstance(value, dict):
            return [(key + '_' + k, v) for k, v in flatten_dict(value).items()]
        else:
            return [(key, value)]

    items = [item for k, v in d.items() for item in expand(k, v)]
    return dict(items)

# Flatten each data item
flattened_data = [flatten_dict(item) for item in data]

# Convert the flattened data to a Pandas DataFrame
new_df = pd.DataFrame(flattened_data)

# Convert coordinates array to string for CSV compatibility
new_df['geometry_coordinates'] = new_df['geometry_coordinates'].apply(str)

# Get current datetime
current_datetime = datetime.now()

# Add the datetime to each row as the first column
new_df.insert(0, 'Current_Datetime', current_datetime)

# Remove 'type' and 'geometry_type' columns
new_df = new_df.drop(columns=['type', 'geometry_type'])

# Append the new data to the existing DataFrame
combined_df = pd.concat([existing_df, new_df], ignore_index=True)

# Save the combined DataFrame back to the CSV file
combined_df.to_csv(csv_file_path, index=False)



# -------------------------------------------------
# SOURCE
# -------------------------------------------------
d = EsriDumper(
    "https://services2.arcgis.com/WLyMuW006nKOfa5Z/ArcGIS/rest/services/RCS_Status_PUBLIC/FeatureServer/0"
)

# -------------------------------------------------
# STYLE CONFIG
# -------------------------------------------------
STATUS_FILL = {
    "Very Good": "#00a651",                  # green
    "Good": "#8fd18f",                       # light green
    "Fair": "#ffa500",                       # orange
    "Poor": "#ff0000",                       # red
    "Closed": "#000000",                     # black
    "Closed for the Season": "#000000",      # black
    "Snow Covered": "#ffffff",               # white
    "Walking Only (Skateway closed)": "#808080",  # grey
}

DEFAULT_STYLE = {
    "stroke": "#cccccc",
    "stroke-width": 2,
    "stroke-opacity": 1,
    "fill": "#cccccc",
    "fill-opacity": 0.5,
}

STROKE_WIDTH = 2
STROKE_OPACITY = 1
FILL_OPACITY = 0.5


# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def get_status(properties: dict):
    """Return Status value with case-insensitive lookup."""
    for key in ("Status", "status", "STATUS"):
        if key in properties:
            return properties.get(key)

    for k, v in properties.items():
        if isinstance(k, str) and k.lower() == "status":
            return v

    return None


def apply_style(properties: dict, status_value):
    fill = STATUS_FILL.get(str(status_value).strip() if status_value else None)

    if fill is None:
        properties.update(DEFAULT_STYLE)
        return

    properties["fill"] = fill
    properties["fill-opacity"] = FILL_OPACITY
    properties["stroke"] = fill              # ← same as fill
    properties["stroke-width"] = STROKE_WIDTH
    properties["stroke-opacity"] = STROKE_OPACITY


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    features = []
    unknown_statuses = {}

    for feature in d:
        props = feature.get("properties", {})
        status_val = get_status(props)

        status_key = str(status_val).strip() if status_val else None
        if status_key and status_key not in STATUS_FILL:
            unknown_statuses[status_key] = unknown_statuses.get(status_key, 0) + 1

        apply_style(props, status_val)

        features.append({
            "type": "Feature",
            "geometry": feature.get("geometry"),
            "properties": props
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open("status_styled.geojson", "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    print(f"Wrote {len(features)} features to status_styled.geojson")

    if unknown_statuses:
        print("Unknown status values encountered:")
        for k, v in unknown_statuses.items():
            print(f"  - {k}: {v}")


if __name__ == "__main__":
    main()


import pandas as pd

# -------------------------------------------------
# Source CSV (GitHub raw)
# -------------------------------------------------
CSV_URL = "https://raw.githubusercontent.com/PatLittle/skateway_data/main/current_conditions.csv"

# -------------------------------------------------
# Fixed test window
# -------------------------------------------------
START_UTC = pd.to_datetime("2025-12-27 00:00:00", utc=True)
END_UTC   = datetime.now(timezone.utc)
# -------------------------------------------------
# Columns (explicit)
# -------------------------------------------------
DT_COL = "Current_Datetime"
FROM_COL = "properties_From_"
TO_COL = "properties_To_"
ID_COL = "properties_ID"
STATUS_COL = "properties_Status"

# -------------------------------------------------
# Status → task ID mapping (IDs are symbolic, not unique)
# -------------------------------------------------
STATUS_CODE = {
    "Very Good": "vg",
    "Good": "g",
    "Fair": "f",
    "Poor": "p",
    "Snow Covered": "sc",
    "Walking Only (Skateway closed)": "wo",
    "Closed": "c",
    "Closed for the Season": "cs",
}
UNKNOWN_CODE = "unk"

# -------------------------------------------------
# Load + parse
# -------------------------------------------------
df = pd.read_csv(CSV_URL)

df[DT_COL] = pd.to_datetime(df[DT_COL], errors="coerce", utc=True)
df = df.dropna(subset=[DT_COL])

df = df[(df[DT_COL] >= START_UTC) & (df[DT_COL] <= END_UTC)].copy()

df[ID_COL] = pd.to_numeric(df[ID_COL], errors="coerce").astype("Int64")
df = df.dropna(subset=[ID_COL])
df[ID_COL] = df[ID_COL].astype(int)

df[STATUS_COL] = df[STATUS_COL].astype(str).str.strip()
df["status_code"] = df[STATUS_COL].map(STATUS_CODE).fillna(UNKNOWN_CODE)

df = df.sort_values([ID_COL, DT_COL])

# -------------------------------------------------
# Helper
# -------------------------------------------------
def fmt_ts(ts: pd.Timestamp) -> str:
    return ts.strftime("%Y-%m-%d %H:%M:%S")

# -------------------------------------------------
# Build Mermaid Gantt
# -------------------------------------------------
header = """
```mermaid
---
topAxis: true
displayMode: compact
config:
  themeCSS: " #vg { fill: Green } #g {fill: yellow} #f {fill: orange} #p {fill: red}      \\n
#c {fill: Black} #cs {fill: Black} #sc {fill: White} #wo {fill: saddlebrown} \\n
            text[id^=cs] { fill: red; } text[id^=sc] { fill: red; }
        "
---
"""
lines = [header]

lines.append("gantt")
lines.append("  title Skateway segment statuses (2025-12)")
lines.append("  dateFormat  YYYY-MM-DD HH:mm:ss")
lines.append("  axisFormat  %Y %m %d")

for pid, g in df.groupby(ID_COL, sort=True):
    g = g.reset_index(drop=True)

    # Section name = From->To (first non-empty in window)
    from_val = next((v for v in g[FROM_COL] if str(v).strip()), "")
    to_val   = next((v for v in g[TO_COL] if str(v).strip()), "")
    section = f"{from_val}-{to_val}".strip("-") or "Unknown-Unknown"

    lines.append(f"  section {section}")

    run_start = g.loc[0, DT_COL]
    run_status = g.loc[0, STATUS_COL]
    run_code = g.loc[0, "status_code"]

    for i in range(1, len(g)):
        if g.loc[i, "status_code"] != run_code:
            run_end = g.loc[i, DT_COL]
            # TASK TEXT = STATUS (human-readable)
            # TASK ID   = status code (vg, g, f, etc.)
            lines.append(
                f"  {run_status}: {run_code}, {fmt_ts(run_start)}, {fmt_ts(run_end)}"
            )
            run_start = g.loc[i, DT_COL]
            run_status = g.loc[i, STATUS_COL]
            run_code = g.loc[i, "status_code"]

    # Final run extends to end of window
    lines.append(
        f"  {run_status}: {run_code}, {fmt_ts(run_start)}, {fmt_ts(END_UTC)}"
    )

lines.append("```")

mermaid_md = "\n".join(lines)

# -------------------------------------------------
# Write to gantt.md
# -------------------------------------------------
with open("gantt.md", "w", encoding="utf-8") as f:
    f.write(mermaid_md + "\n")

print("Wrote gantt.md")

import json
import pandas as pd
import plotly.express as px



url = "https://github.com/PatLittle/skateway_data/raw/refs/heads/main/status_styled.geojson"

# --- load geojson (requests) ---
import requests
gj = requests.get(url, timeout=30).json()

# Build a small table that links each feature to a row via OBJECTID (or ID)
rows = []
for f in gj["features"]:
    p = f.get("properties", {})
    rows.append({
        "OBJECTID": p.get("OBJECTID"),
        "ID": p.get("ID"),
        "Status": p.get("Status"),
        "From": p.get("From_"),
        "To": p.get("To_"),
        "fill": p.get("fill"),  # already a hex like "#000000"
    })
df = pd.DataFrame(rows)

# Make a status->color map using the GeoJSON's own "fill" values
status_color_map = (
    df.dropna(subset=["Status", "fill"])
      .drop_duplicates("Status")
      .set_index("Status")["fill"]
      .to_dict()
)

fig = px.choropleth_mapbox(
    df,
    geojson=gj,
    featureidkey="properties.OBJECTID",  # ties geojson feature -> df row
    locations="OBJECTID",
    color="Status",
    color_discrete_map=status_color_map,
    hover_data={"Status": True, "From": True, "To": True, "OBJECTID": True, "fill": False},
    mapbox_style="carto-positron",
    opacity=0.6,
    center={"lat": 45.41, "lon": -75.69},
    zoom=13.75,
)

fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))


from datetime import datetime

rendered_at = datetime.now().strftime("%Y-%m-%d %H:%M")

fig.update_layout(
    title=dict(
        text=f"Skateway Segment Statuses — rendered {rendered_at}",
        x=0.5,
        y=0.95,
        xanchor="center",
        font=dict(size=32)  # matches doubled legend scale nicely
    ),
    legend=dict(
        x=0.01,
        y=0.01,
        xanchor="left",
        yanchor="bottom",
        font=dict(size=28)
    )
)

fig.write_image(
    "skateway_status_map.png",
    width=1600,
    height=1200,
    scale=2
)
