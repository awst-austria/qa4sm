Geojson file preparation for datasets
=====================================

QA4SM expects a [geojson](https://datatracker.ietf.org/doc/html/rfc7946) file called `geoinfo.json` in the root folder of each dataset. 
This file shall contain all data to be displayed on the map.

Example geojson file for an ISMN dataset:
```json
{
    "type": "FeatureCollection",
    "features":
    [
        {
            "type": "Feature",
            "geometry":
            {
                "type": "Point",
                "coordinates":
                [
                    12.3155,
                    45.4408
                ]
            },
            "properties":
            {
                "markerColor": "#00aa00",
                "datasetProperties":
                [
                    {
                        "propertyName": "Network",
                        "propertyValue": "network name"
                    },
                    {
                        "propertyName": "depth_from",
                        "propertyValue": "0.0"
                    },
                    {
                        "propertyName": "depth_to",
                        "propertyValue": "0.05"
                    },
                    {
                        "propertyName": "timerange_from",
                        "propertyValue": "2010-01-29 08:00:00"
                    },
                    {
                        "propertyName": "timerange_to",
                        "propertyValue": "2010-01-30 01:00:00"
                    }
                ]
            }
        },
        {
            "type": "Feature",
            "geometry":
            {
                "type": "Point",
                "coordinates":
                [
                    16.7855,
                    45.4408
                ]
            },
            "properties":
            {
                "markerColor": "#00aa00",
                "datasetProperties":
                [
                    {
                        "propertyName": "Network",
                        "propertyValue": "network name"
                    },
                    {
                        "propertyName": "depth_from",
                        "propertyValue": "0.0"
                    },
                    {
                        "propertyName": "depth_to",
                        "propertyValue": "0.5"
                    },
                    {
                        "propertyName": "timerange_from",
                        "propertyValue": "2010-01-29 08:00:00"
                    },
                    {
                        "propertyName": "timerange_to",
                        "propertyValue": "2010-01-30 01:00:00"
                    }
                ]
            }
        },
        {
            "type": "Feature",
            "geometry":
            {
                "type": "Point",
                "coordinates":
                [
                    21.2555,
                    45.4408
                ]
            },
            "properties":
            {
                "markerColor": "#00aa00",
                "datasetProperties":
                [
                    {
                        "propertyName": "Network",
                        "propertyValue": "CARBOAFRICA"
                    },
                    {
                        "propertyName": "depth_from",
                        "propertyValue": "0.1"
                    },
                    {
                        "propertyName": "depth_to",
                        "propertyValue": "0.8"
                    },
                    {
                        "propertyName": "timerange_from",
                        "propertyValue": "2010-01-29 08:00:00"
                    },
                    {
                        "propertyName": "timerange_to",
                        "propertyValue": "2010-01-30 01:00:00"
                    }
                ]
            }
        }
    ]
}
```

In the above example we have 3 *features*, each feature represents an ISMN station. The geometry for a station is always a **Point**.
Each feature in a geojson file can include a `properties` field for storing additional data related to that specific feature.
The geojson file above has the following properties:   

`markerColor`: Color for the station marker on the map. (hex color code)   
`datasetProperties`: This is a dictionary for properties to be displayed in a small table when the user hovers over the marker in the map.
For the ISM dataset, the `Network`, `depth_from` and `depth_to` properties are also used for filtering. Only those stations will be displayed on tha map which match the Station and Dept filter settings.
If these properties are not defined for a station, it will be displayed on the map, regardless of the filter configuration.


Example geojson file for satellite datasets:

```json
{
    "type": "FeatureCollection",
    "features":
    [
        {
            "type": "Feature",
            "geometry":
            {
                "type": "Polygon",
                "coordinates":
                [
                    [
                        [
                            8.483423847386291,
                            51.72749070079038
                        ],
                        [
                            8.483423847386291,
                            50.290689077221515
                        ],
                        [
                            10.915286153501029,
                            50.290689077221515
                        ],
                        [
                            8.483423847386291,
                            51.72749070079038
                        ]
                    ]
                ]
            },
            "properties":
            {
                "markerColor": "#00aa00",
                "datasetProperties":
                [
                    {
                        "propertyName": "Sat prop 1",
                        "propertyValue": "Value 4"
                    },
                    {
                        "propertyName": "Sat prop 2",
                        "propertyValue": "Value 5"
                    },
                    {
                        "propertyName": "Sat prop 3",
                        "propertyValue": "Value 6"
                    }
                ]
            }
        }
    ]
}
```
A geoinfo file for a satellite dataset is essentially the same as for ISMN, there are only 2 differences:
- The geometry type is `polygon` and the coordinates should form a polygon on the map that represents the coverage of the dataset. Please note that the first and last coordinates has to be the same.
- Properties in the `datasetProperties` block are not used for filtering.