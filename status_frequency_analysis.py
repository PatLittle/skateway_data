import pandas as pd
import plotly.express as px

# Read the data
df = pd.read_csv('current_conditions.csv')

# Convert Current_Datetime to datetime type
df['Current_Datetime'] = pd.to_datetime(df['Current_Datetime'])

# Get 100 most recent distinct dates
recent_dates = df['Current_Datetime'].unique()
recent_dates = sorted(recent_dates, reverse=True)[:173]
df = df[df['Current_Datetime'].isin(recent_dates)]

# Get frequency counts
status_counts = df.groupby(['Current_Datetime', 'properties_Status']).size().unstack(fill_value=0)

# Define color mapping
color_map = {
    'Closed for the Season': '#202020',  # dark grey
    'Closed': '#333533',                 # medium grey
    'Poor': '#f35b04',                   # light red
    'Fair': '#f7b801',                   # pale orange
    'Good': '#7678ed',                   # light purple
    'Very Good': '#3d348b',              # purple
    'Snow Covered': '#f6fff8',           # white
    'Walking Only (Skateway closed)': '#d08c60'  # red
}

# Create stacked bar chart
fig = px.bar(status_counts, 
             barmode='stack',
             title='Skateway Status Over Time (Last 170 Records)',
             labels={'value': 'Count',
                    'Current_Datetime': 'Date',
                    'properties_Status': 'Status'},
             color_discrete_map=color_map)  # Apply custom colors

# Improve layout
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Count",
    legend_title="Status",
    bargap=0,  # Remove space between bars
    bargroupgap=0  # Remove space between bar groups
)

# Save as SVG
fig.write_image('skateway_status_frequency.svg')

# Save as HTML with WebGL renderer
config = {'toImageButtonOptions': {'format': 'svg'},
         'plotGlPixelRatio': 2,
         'scrollZoom': True}
fig.write_html('skateway_status_frequency_webgl.html', config=config)

# Print the frequency counts
print("\nFrequency counts by date:")
print(status_counts)
