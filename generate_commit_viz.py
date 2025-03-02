import pandas as pd
import svgwrite
from git import Repo
from datetime import datetime, timedelta

# Repository and file paths
repo_path = '.'  # Assumes script runs in the repo directory
csv_file = 'current_conditions.csv'

# Initialize Git repository
repo = Repo(repo_path)

# Get all commits modifying the CSV file
commits = list(repo.iter_commits(paths=csv_file))

# Function to load CSV content at a specific commit
def get_csv_at_commit(commit):
    content = commit.tree / csv_file
    return pd.read_csv(content.data_stream, index_col='properties_OBJECTID')

# Get the current list of properties_OBJECTID from the latest commit
current_df = get_csv_at_commit(commits[0])  # Latest commit is first
object_ids = sorted(current_df.index.tolist())  # Sort for consistency

# Initialize a dictionary to track changes per day over the last 30 days
today = datetime.now().date()
changes_per_day = { (today - timedelta(days=i)): set() for i in range(30) }

# Process commits in chronological order
commits = sorted(commits, key=lambda c: c.committed_datetime)
previous_df = None
for commit in commits:
    commit_date = commit.committed_datetime.date()
    current_df = get_csv_at_commit(commit)
    
    if previous_df is not None:
        # Identify rows that changed between commits
        # Merge to handle added/removed rows; fill NaN for comparison
        merged = previous_df.reindex(current_df.index).fillna('N/A').ne(
                 current_df.reindex(previous_df.index).fillna('N/A'))
        changed = merged.any(axis=1)
        changed_ids = changed[changed].index.tolist()
        
        # Record changes if within the last 30 days
        if commit_date in changes_per_day:
            changes_per_day[commit_date].update(changed_ids)
    
    previous_df = current_df.copy()

# Generate SVG visualization
cell_size = 10  # Size of each cell in pixels
width = 30 * cell_size  # 30 days
height = len(object_ids) * cell_size  # One row per OBJECTID
dwg = svgwrite.Drawing('commit_graph.svg', profile='tiny', size=(width + 50, height + 20))

# Add day labels (day of month) at the top
for j in range(30):
    day = today - timedelta(days=29 - j)
    dwg.add(dwg.text(str(day.day), insert=(j * cell_size + 2, 10), font_size=8))

# Draw the grid
for i, obj_id in enumerate(object_ids):
    for j in range(30):
        day = today - timedelta(days=29 - j)
        fill_color = 'green' if obj_id in changes_per_day[day] else 'lightgray'
        rect = dwg.rect((j * cell_size, i * cell_size + 20), (cell_size - 1, cell_size - 1), fill=fill_color)
        rect['title'] = f"ID: {obj_id}, Date: {day}"  # Tooltip on hover
        dwg.add(rect)

# Save the SVG file
dwg.save()
