import pandas as pd
from datetime import datetime

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
