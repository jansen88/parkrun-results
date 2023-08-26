import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import html, Dash
from dash_extensions.javascript import assign

import json
import geopandas as gpd

from parkrun.load_data import get_parkrun_locations

# Get parkrun locations json and convert to geojson
features = get_parkrun_locations()
locations = gpd.GeoDataFrame.from_features(features)
geojson = json.loads(locations.to_json())

# Javascript function to draw marker
draw_icon = assign("""function(feature, latlng){
const icon = L.icon({iconUrl: `https://png2.cleanpng.com/sh/9b546064281f59a87568ea77eb528d3a/L0KzQYm3V8AyN6Vqi5H0aYP2gLBuTfNwdaF6jNd7LXnmf7B6TfRwf59xh9NtLUXlQ4q6hsE0QGE5ftM8LkC4RoKAWcc4OWY4SKYCOEO4RYa5VcYveJ9s/kisspng-computer-icons-download-5b393f13804fa3.0561797715304783555256.png`, iconSize: [48, 48]});
return L.marker(latlng, {icon: icon});
}""")

app = Dash()
app.layout = html.Div(children=[
                        dl.Map(center=[39, -98],
                               zoom=4,
                               children=[
                                    dl.TileLayer(),
                                    dl.GeoJSON(
                                        data=dlx.geojson_to_geobuf(geojson), 
                                        format='geobuf',
                                        cluster=True,
                                        # options=dict(pointToLayer=draw_icon)
                                    ),
                            ],
                            style={'width': '100%', 'height': '100vh'})])

if __name__ == "__main__":
    app.run_server(debug=False)

# import geopandas as gpd
# import dash_leaflet as dl
# import dash_leaflet.express as dlx
# from dash import Dash, html, Output, Input
# import json

# location = gpd.GeoDataFrame(geometry=gpd.points_from_xy([-74.0060], [40.7128]))
# app = Dash()
# app.layout = html.Div(
#                     children=[
#                         dl.Map(
#                             center=[39, -98], 
#                             zoom=4, 
#                             children=[
#                                 dl.TileLayer(),
#                                 dl.GeoJSON(data=dlx.geojson_to_geobuf(json.loads(location.to_json())), format='geobuf', id='locations', zoomToBoundsOnClick=True)], 
#                             style={'width': '100%', 'height': '80vh'}, id="map"),
#                         ])

# if __name__ == "__main__":
#     app.run_server(debug=True)