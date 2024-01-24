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
combined_df = existing_df.append(new_df, ignore_index=True)

# Save the combined DataFrame back to the CSV file
combined_df.to_csv(csv_file_path, index=False)
