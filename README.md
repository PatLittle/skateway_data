The ice conditions data shown on the map can be accessed from the ESRI feature layer [here](https://services2.arcgis.com/WLyMuW006nKOfa5Z/ArcGIS/rest/services/RCS_Status_PUBLIC/FeatureServer/0).


[Esri Dump](https://pypi.org/project/esridump/). This allows you to quickly dump a ESRI REST endpoint to GeoJSON. 

```python

import json
from esridump.dumper import EsriDumper

d = EsriDumper('http://example.com/arcgis/rest/services/Layer/MapServer/1')

# Iterate over each feature
for feature in d:
    print(json.dumps(feature))

d = EsriDumper('http://example.com/arcgis/rest/services/Layer/MapServer/2')

# Or get all features in one list
all_features = list(d)

```
Here is an example of the python, and feel free to use this as the starting point for your own experiment transforming geo data to tabular.


<a href="https://colab.research.google.com/gist/PatLittle/413eef25fae1d1a2e1d5be7ee38c79d0/dump-canal-esri.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

View the Data Data --> [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/PatLittle/skateway_data)

This technique using Esri Dump should be reusable with a huge number of Geospatial datasets from the Open Maps collection on Open.Canada.ca.

--------
![image](https://github.com/user-attachments/assets/0ee1ea3d-0cac-47b3-8e8c-2f10c7fd1c74)

* [LinkedIn Version](https://www.linkedin.com/pulse/opendatadays-geospatial-data-non-geo-users-patrick-little-mba-udclc/)
* 