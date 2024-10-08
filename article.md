 ## #OpenDataDays - Geospatial Data for non-geo data users

 > In the Government of Canada open data ecosystem some of the most interesting, high quality, frequently updated, data comes out of geospatial community. For data users without a background in geospatial, it can be a challenge to figure out how to integrate geospatial sources into their normal workflows.

Back in late January I was getting excited for the ❄️skating season⛸️ on the Rideau Canal here in Ottawa. I thought it would be an interesting personal project to capture the ice conditions overtime, and see what I could do with the data at the end of the season.

The National Capital Commission - Commission de la capitale nationale has a great ArcGIS map showing the ice conditions and is kept updated reliably. But how could I get the data from the map into a format I was comfortable working with? 


After some poking around and searching in the usual places, I came across a python package [Esri Dump](https://pypi.org/project/esridump/). This allows you to quickly dump a ESRI REST endpoint to GeoJSON. 

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
From there I was back in my comfort zone, using basic techniques to flatten JSON to tabular data. The ice conditions data shown on the map can be accessed from the ESRI feature layer [here](https://services2.arcgis.com/WLyMuW006nKOfa5Z/ArcGIS/rest/services/RCS_Status_PUBLIC/FeatureServer/0).

Here is an example of the python, and feel free to use this to follow along, or as the starting point for your own experiment transforming geo data to tabular.


<a href="https://colab.research.google.com/gist/PatLittle/413eef25fae1d1a2e1d5be7ee38c79d0/dump-canal-esri.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>


This technique using Esri Dump should be reusable with a huge number of Geospatial datasets from the Open Maps collection on Open.Canada.ca. If you are able to use this technique to explore GC open data in a new way, I'd encourage you to share using the hashtag #OpenDataDay ❤️ 

--------

More to come - in the next installment we will explore how we can use free tools automatically capture the data over time. 

--------

>  Open Data Day (ODD) is an annual celebration of open data all over the world. Groups from likely every country create local events on 
> the day where they will use open data in their communities. ODD is led by the Open Knowledge Foundation (OKFN) and this year’s edition   
> runs from 2-8 March 2024.

[![Open Data Day](https://media.licdn.com/dms/image/sync/v2/D4E27AQFBjQG-lMjuKw/articleshare-shrink_800/articleshare-shrink_800/0/1711125094802?e=1728964800&v=beta&t=5NGIzvZR2BLKl3JeyAX5lmNreirNuLIonnhBoTziKvU)](https://opendataday.org)



**Disclaimer** *- The views expressed here are my own, and don’t represent the opinions of my team or my employer.*
