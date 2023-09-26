## Maddie Henderson - Aug 2023
## Make an interactive map to export to html
'''
### TODO
# https://stackoverflow.com/questions/58227034/png-image-not-being-displayed-on-folium-map
# Display a graph of the recovery rate at selected points
# add colorbar that's not ugly
# popup color https://stackoverflow.com/questions/62789558/is-it-possible-to-change-the-popup-background-colour-in-folium

# colorbar from my own image 
zoom level better
names shorter and bettter 
example graphs 
change color of TIST groves fill (no fill?) 
Did i already remove the roads etc from this ?? or are they so light? is this exposing more method flaws lol

'''
# import pandas as pd 
import folium as f
from folium.features import GeoJsonPopup, GeoJsonTooltip
from folium.plugins import FloatImage
from folium import IFrame
import pickle
import base64

###################################################3
# Define the center of map
lon, lat = 37.79, -0.24  #EDIT THIS TO BE ON THARAKA # 37.61, 0.18 for overall map

tile = f.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True, 
        show = True, 
       )

my_map = f.Map(location=[lat, lon], zoom_start=10, tiles = tile)

#for all the bounding boxes of images in the ROI
# t_bounds = [[-0.9639821313886587, 36.11092694867859], [0.8877151637669112, 38.47870637456082]] #original ROI
t_bounds = [[-0.470,37.400],[0.100, 38.300]] #for tharaka pngs from QGIS

############################################################
# TIST groves and counties

with open('tist_and_counties_gp.pkl', 'rb') as file:
   tist_gp, counties_gp= pickle.load(file)

# select = np.round(np.random.rand(5000) * 30000, 0).astype('int16')# get 5000 random tist groves
#reduced for putting on web
tist_gp = tist_gp.loc[tist_gp['COUNTY'] == 'Tharaka', ['Trees', 'Name', 'geometry']] #get only those in Tharaka 


f.GeoJson(tist_gp, name='TIST Groves',
        style_function= lambda x: {"fillColor": "#00cc66", "fillOpacity": 0.0,
                                   "weight": 1, "color": "#000000"}).add_to(my_map)


##################################################################################3
# RASTER LAYERS

f.raster_layers.ImageOverlay('./external_programs/thar_highres_59.png', 
                  bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]]
                  name = 'Recovery rates 59 (Apr 2019)',
                  overlay = True,
                  control = True, 
                  show = True, 
                  ).add_to(my_map)

f.raster_layers.ImageOverlay('./external_programs/thar_highres.png', 
                  bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]]
                  name = 'Recovery rates 77 (Oct 2019)',
                  overlay = True,
                  control = True, 
                  show = True, 
                  ).add_to(my_map)

################################################################
# EXAMPLE GRAPHS
width = 560
height = 330
loc1 = [-0.310604, 37.807015]
encoded = base64.b64encode(open('ex_graph1.png', 'rb').read())

''' #PNG html version -- leads to much worse quality
html = '<img src="data:image/png;base64,{}">'.format
iframe = IFrame(html(encoded.decode("UTF-8")), width=(width)+20, height=(height)+20)
'''
## SVG version
svg = """
<object data="data:image/png;base64,{}" width="{}" height="{} type="image/svg+xml">
</object>""".format
iframe = IFrame(svg(encoded.decode('UTF-8'), width, height) , width=width+20, height=height+20)
popup = f.Popup(iframe, max_width=2650)

icon = f.Icon(color="purple", icon = 'comment')
marker = f.Marker(location=loc1, popup=popup, icon=icon)
marker.add_to(my_map)


###############################################################
# FINISH AND SAVE

FloatImage('legend_smaller.png', bottom=1, left=1).add_to(my_map)
#colormap legend since its kinda hard to make te he 

f.map.LayerControl().add_to(my_map)

my_map.save('tharaka_interactive_map.html')

print('donezo')