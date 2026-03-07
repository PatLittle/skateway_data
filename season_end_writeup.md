# Skateway Season-End EDA (from `current_conditions.csv`)


## Executive summary


- The latest season (2025-2026) averaged **53.13% open network coverage**, which is **-9.92 points** versus 2024-2025.

- Average **Very Good coverage** in 2025-2026 was **26.91%**, a **-18.64 point** year-over-year change.

- The >=50% open period in 2025-2026 lasted **60 days**, showing a long mid-season usability window despite frequent weather resets.


## Season-level comparison


| season    |   snapshots | first_snapshot             | last_snapshot              |   avg_open_km |   peak_open_km |   avg_open_pct |   peak_open_pct |   avg_very_good_pct |
|:----------|------------:|:---------------------------|:---------------------------|--------------:|---------------:|---------------:|----------------:|--------------------:|
| 2023-2024 |         105 | 2024-01-24 03:37:31.941580 | 2024-02-27 00:32:10.939937 |          0.89 |           6.29 |           5.48 |           38.91 |                0    |
| 2024-2025 |         192 | 2025-01-10 07:41:44.802344 | 2025-03-14 16:09:56.401991 |         10.21 |          16.2  |          63.05 |          100    |               45.55 |
| 2025-2026 |         216 | 2025-12-27 19:17:23.272797 | 2026-03-07 02:04:26.219374 |          8.63 |          15.84 |          53.13 |           97.51 |               26.91 |


## Status mix by season (length-weighted share %)


| properties_Status              |   2023-2024 |   2024-2025 |   2025-2026 |
|:-------------------------------|------------:|------------:|------------:|
| Closed                         |       91.66 |       24.63 |       23.16 |
| Closed for the Season          |        2.86 |        0.04 |        5.17 |
| Fair                           |        0    |        6.78 |        8.95 |
| Good                           |        0    |        8.63 |       14.14 |
| Poor                           |        5.48 |        2.08 |        3.15 |
| Snow Covered                   |        0    |        5.5  |       18.51 |
| Very Good                      |        0    |       45.55 |       26.91 |
| Walking Only (Skateway closed) |        0    |        6.77 |        0    |


## Core timing metric: >=50% network open


| season    | first_50pct_open   | last_50pct_open   |   days_between |
|:----------|:-------------------|:------------------|---------------:|
| 2023-2024 | n/a                | n/a               |              0 |
| 2024-2025 | 2025-01-11         | 2025-03-05        |             52 |
| 2025-2026 | 2026-01-03         | 2026-03-05        |             60 |


## Segment reliability (open snapshot %)



### 2023-2024

Worst 3 segments

| properties_From_   | properties_To_   |   open_snapshot_pct |
|:-------------------|:-----------------|--------------------:|
| Bank               | Bronson          |                   0 |
| Bronson            | Dows Lake        |                   0 |
| Dows Lake          | Library          |                   0 |

Best 3 segments

| properties_From_   | properties_To_   |   open_snapshot_pct |
|:-------------------|:-----------------|--------------------:|
| Fifth              | Lansdowne        |               17.14 |
| Lansdowne          | Bank             |               17.14 |
| Pretoria           | Fifth            |               17.14 |


### 2024-2025

Worst 3 segments

| properties_From_   | properties_To_   |   open_snapshot_pct |
|:-------------------|:-----------------|--------------------:|
| Mackenzie King     | Laurier          |               68.75 |
| Rideau             | Mackenzie King   |               68.75 |
| Bank               | Bronson          |               70.83 |

Best 3 segments

| properties_From_   | properties_To_   |   open_snapshot_pct |
|:-------------------|:-----------------|--------------------:|
| Patterson Creek    | Patterson Creek  |               79.69 |
| Pretoria           | Fifth            |               79.69 |
| Waverley           | Concord          |               79.69 |


### 2025-2026

Worst 3 segments

| properties_From_   | properties_To_   |   open_snapshot_pct |
|:-------------------|:-----------------|--------------------:|
| Laurier            | Waverley         |                0    |
| Patterson Creek    | Patterson Creek  |                0.46 |
| Bank               | Bronson          |               68.52 |

Best 3 segments

| properties_From_   | properties_To_   |   open_snapshot_pct |
|:-------------------|:-----------------|--------------------:|
| Pretoria           | Fifth            |               78.7  |
| Waverley           | Concord          |               78.7  |
| Somerset           | Waverley         |               83.33 |


## End-of-season write-up


This season finished with a **usable but more volatile profile** than the prior year. The corridor stayed open across more than half the network for about two months, which is strong from an access perspective. But quality shifted down from 'Very Good' toward 'Good/Fair/Snow Covered' more often.

The year-over-year signal suggests maintenance teams preserved **availability** better than they preserved **top-tier ice quality**. For skaters, that means more days where a trip was possible, but fewer days where conditions were consistently excellent.

Operationally, this points to a useful strategy split for next season: 1) keep current opening responsiveness (which appears effective), and 2) target post-snow recovery speed on segments that repeatedly dropped into Snow Covered or Fair states.

For communications, the data supports emphasizing **real-time condition checks** over static expectations, because quality moved quickly even while the network remained broadly open.
