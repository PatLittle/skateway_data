import pandas as pd
import svgwrite
from git import Repo
from datetime import datetime, timedelta

# Paths
repo_path = '.'
csv_file = 'current_conditions.csv'

# Initialize Git repository
repo = Repo(repo_path)
commits = sorted(repo.iter_commits(paths=csv_file), key=lambda c: c.committed_datetime)

# Helper functions
def get_commit_on_or_before(date):
    for commit in reversed(commits):
        if commit.committed_datetime.date() <= date:
            return commit
    return None

def get_csv_at_commit(commit):
    if commit is None:
        return pd.DataFrame()
    content = commit.tree / csv_file
    return pd.read_csv(content.data_stream, index_col='properties_OBJECTID')

def all_closed(df):
    closed_statuses = {"Closed", "Closed for the season"}
    return df['status'].isin(closed_statuses).all() if not df.empty and 'status' in df.columns else False  # Added check for 'status' column

# Status colors
status_colors = {
    "Open": "green",
    "Closed": "red",
    "Closed for the season": "orange"
}

# Get top N OBJECTIDs from latest commit
latest_commit = commits[-1] if commits else None
current_df = get_csv_at_commit(latest_commit)
object_ids = sorted(current_df.index.tolist())[:10]  # Limit to top 10

# Collect data for last 30 days
today = datetime.now().date()
data_per_day = {}
for i in range(30):
    day = today - timedelta(days=i)
    commit = get_commit_on_or_before(day)
    df = get_csv_at_commit(commit)
    data_per_day[day] = {'df': df, 'all_closed': all_closed(df)}

# SVG dimensions (approximating GitHub size)
cell_size = 10
num_rows = len(object_ids)  # 10 rows
num_cols = 30
width = num_cols * cell_size  # 300px
height = num_rows * cell_size  # 100px
svg_width = 700  # Total width with padding
svg_height = height + 20  # Room for labels

dwg = svgwrite.Drawing('status_grid.svg', size=(f"{svg_width}px", f"{svg_height}px"))

# Add day labels (centered over columns)
for j in range(num_cols):
    day = today - timedelta(days=29 - j)
    dwg.add(dwg.text(str(day.day), insert=(j * cell_size + 2, 10), font_size=8))

# Draw grid
for i, obj_id in enumerate(object_ids):
    for j in range(num_cols):
        day = today - timedelta(days=29 - j)
        day_data = data_per_day[day]
        df = day_data['df']
        all_closed_day = day_data['all_closed']
        
        if all_closed_day:
            fill_color = 'black'
        elif not df.empty and obj_id in df.index and 'status' in df.columns:  # Added check for 'status' column
            status = df.at[obj_id, 'status']
            fill_color = status_colors.get(status, 'lightgray')
        else:
            fill_color = 'lightgray'
        
        rect = dwg.rect((j * cell_size, i * cell_size + 20), 
                        (cell_size - 1, cell_size - 1), fill=fill_color)
        dwg.add(rect)

dwg.save()
