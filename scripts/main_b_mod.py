import networkx as nx
from networkx.classes.function import path_weight
import osmnx as ox
import geopandas
import momepy
import pandas
import folium
import googlemaps
from shapely.geometry import LineString
import numpy
from scipy.spatial.distance import cdist

from scripts.keys import *

gmaps_k = get_key()
gmaps = googlemaps.Client(key=gmaps_k)



# received a raw file, and parses/filters it
def parse_file(signal, raw_file, new_file_name):
    if not signal: return 0 

    # import raw file
    raw_file = geopandas.read_file(raw_file)
    # raw_file = geopandas.read_file(raw_file, bbox=(-74.018326,40.704587,-73.893356,40.817447)) <<-- testing

    # only keep relevant columns
    columns_to_keep = [col for col in raw_file.columns if "geometry" in col or "bike_lane" in col or "physicalid" in col or "bike_trafd" in col or "trafdir" in col or "shape_leng" in col or "rw_type" in col or "snow_pri" in col]

    raw_file = raw_file[columns_to_keep]

    # delete ferry routes (rw_type = 14)
    raw_file = raw_file[~raw_file["rw_type"].isin(["14"])].copy()

    # expand multilinestring to linestring
    raw_file = raw_file.explode(index_parts=True)

    # gives each segment a bike lane weight attribute, a lower numbers signifies a higher priority
    def add_bike_lane_weight(row):
    # Bike class info 
    # Class I (protected/off-street lane) (safest)
    # Class II (adjacent/separated lane) (2nd safest)
    # Class III (marked shared/in-street lane) (3rd safest)

    # Number code info:
    # 1 Class I 
    # 2 Class II
    # 3 Class III
    # 4 Links
    # 5 Class begins I, ends II
    # 6 Class begins II, ends III
    # 7 Stairs
    # 8 Class begins I, ends III
    # 9 Class begins II, ends I
    # 10 Class begins III, ends I
    # 11 Class begins III, end II

    # Priority order
    # 1 Class I                        Priority 1
    # 7 Stairs                         Priority 2
    # 4 Links                          Priority 2
    # 5 Class begins I, ends II        Priority 3
    # 9 Class begins II, ends I        Priority 3
    # 2 Class II                       Priority 4
    # 8 Class begins I, ends III       Priority 5
    # 10 Class begins III, ends I      Priority 5
    # 6 Class begins II, ends III      Priority 6
    # 11 Class begins III, end II      Priority 6
    # 3 Class III                      Priority 7

        if row["bike_lane"] == "1":
            return 1
        elif row["bike_lane"] == "7" or row["bike_lane"] == "4":
            return 2
        elif row["bike_lane"] == "5" or row["bike_lane"] == "9":
            return 3
        elif row["bike_lane"] == "2":
            return 4
        elif row["bike_lane"] == "8" or row["bike_lane"] == "10":
            return 5
        elif row["bike_lane"] == "6" or row["bike_lane"] == "11":
            return 6
        elif row["bike_lane"] == "3":
            return 7
        else:
            return 8
    
    raw_file["bike_lane_weight"] = raw_file.apply(add_bike_lane_weight, axis=1)
    
    # oneway_columns creates an additional edge for each LineString which allows bidirectional path traversal by specifying the boolean column in the GeoDataFrame. If a segment is one-way, then segment's direction must be respected. If it is two-way, segment can be traversed from any direction
    def filter_one_way(row):
        # if bike lane is two way, signal segment is not oneway
        if row["bike_trafd"] == "TW":
            return False

        # if bike lane is not two way, but if street is two way, signal segment is not oneway
        if row["trafdir"] == "TW":
            return False

        # else signal it is one way exclusively
        return True 
    
    raw_file["one_way"] = raw_file.apply(filter_one_way, axis=1)


    def str_to_float(row):
        return float(row["shape_leng"])
    raw_file["shape_leng_float"] = raw_file.apply(str_to_float, axis=1)
    

    # Save file 
    raw_file.to_file(new_file_name, driver='GeoJSON')
        
        
# given a text address, it geocodes it to long/lat pair, then finds and returns the closest node in the graph
def geocode_closest_node(address, road_network_file):
    geocode_result = gmaps.geocode(address) # returns a data structure of the given text address using google maps API
    
    # grab address' long and lat
    geocode_result = [geocode_result[0]["geometry"]["location"]["lng"], geocode_result[0]["geometry"]["location"]["lat"]]

    # given a road network file, return those elements/nodes that are within a certain bounded box of the given coordinates
    # these elements will be filtered to find the node closest to the given address
    bbox = geopandas.read_file(road_network_file, bbox=bounded_box(geocode_result[0], geocode_result[1])) 

    min_distance = 1000 # dummy value
    closest_node = 0 # dummy value
    for row in range(len(bbox)):
        # lefmost coordinate
        node1 = [list(bbox.loc[row]["geometry"].coords)[0]]
        # rightmost coordinate
        node2 = [list(bbox.loc[row]["geometry"].coords)[len(list(bbox.loc[row]["geometry"].coords)) - 1]]
        # if distance between node and geocode is lesser, re-assign 
        if cdist(node1, [geocode_result]) < min_distance: 
            min_distance = cdist(node1, [geocode_result])
            closest_node = node1
        if cdist(node2, [geocode_result]) < min_distance: 
            min_distance = cdist(node2, [geocode_result])
            closest_node = node2
    
    return closest_node

# returns a bounded box around a coordinate pair, with a determined radius
def bounded_box(lat, long):
    Rad = .05 # radius in miles

    # calculate bounding box coordinates with geodetic approximation (WGS84)
    a = 6378137 # Radius of earth at equator (m)
    e2 = 0.00669437999014 # eccentricity squared
    m = 1609.344 # 1 mile in meters
    r = numpy.pi / 180 # convert to radians
    #Distance of 1° latitude (miles)
    d1 = r * a * (1 - e2) / (1 - e2 * numpy.sin(lat * r) ** 2) ** (3 / 2) / m
    #Distance of 1° longitude (miles)
    d2 = r * a * numpy.cos(lat * r) / numpy.sqrt(1 - e2 * numpy.sin(lat * r) ** 2) / m

    #Bounding box coordinates
    minLat, maxLat = [lat - Rad / d1, lat + Rad / d1]
    minLon, maxLon = [long - Rad / d2, long + Rad / d2]
    bbox = (minLat, minLon, maxLat, maxLon)
    return bbox

# converts a path (array) to a geodataframe
def path_to_gdf(path):
    path_latitute = [] # store shortest path's lat coords
    for i in range(len(path)):
        path_latitute.append(path[i][1])
        
    path_longitute = [] # store shortest path's long coords
    for i in range(len(path)):
        path_longitute.append(path[i][0])

    # make shortest path a dataframe
    path_df = pandas.DataFrame(
        {
            "Latitude": path_latitute,
            "Longitude": path_longitute,
        }
    )
    # convert to geodataframe
    path_gdf = geopandas.GeoDataFrame(
        path_df, geometry=geopandas.points_from_xy(path_df.Longitude, path_df.Latitude), crs="EPSG:4326"
    )
    # convert to linestring
    lineStringObj = LineString([[a.x, a.y] for a in path_gdf.geometry.values])
    line_df = pandas.DataFrame()
    line_df['Attrib'] = [1,]
    line_gdf = geopandas.GeoDataFrame(line_df, geometry=[lineStringObj,])
    return line_gdf

# returns an html map given a network and a path
def create_map(network, path):
    # create map of road network
    road_map = network.explore()
    
    # overlay path on map
    path.explore(m=road_map, color="red")

    # use folium to add alternative tiles
    folium.TileLayer(show=True).add_to(
        road_map
    )  
    # use folium to add layer control
    folium.LayerControl().add_to(road_map) 

    html_content = road_map._repr_html_()
    return html_content  

# When creating a graph, it will direct edges between nodes in a certain direction. When a route is being created, the directions of the edges must be followed, edges can't be traveled in the wrong way. When calculating a route in road networks, this is used to correctly follow the direction of traffic. The graph automatically direct edges given the coordinates arragement, starting from left to right. For example, the segment with coordinates [(a, b), (c, d)] will direct (a, b)--->(c, d).
# However, the road network file provided does not arrange the coordinate in the direction of traffic. Thus, if the attribute shows TF (indicating flow of traffic is against the arrangement of coordinate), this function reverses them for accurate direction of edges
def arrange_coordinates_direction(file):
# trafdir: Indicates the flow of traffic relative to the street segment's address range.
# FT - With
# TF - Against
# TW - Two-Way
# NV - Non-Vehicular
    for idx, row in file.iterrows():
        traf_dir = file.iloc[idx]["trafdir"]
        prev_coords = list(file.iloc[idx]["geometry"].coords) 
        if traf_dir == "TF" and len(prev_coords) <= 2:  
            file.at[idx, "geometry"] = LineString([prev_coords[1], prev_coords[0]])
        elif traf_dir == "TF":
            coord_len = len(prev_coords) - 1
            reverse_coord = []
            while coord_len >= 0: 
                reverse_coord.append(prev_coords[coord_len])
                coord_len -= 1
            file.at[idx, "geometry"] = LineString(reverse_coord)

    mod_file = file

    return mod_file

# returns the estimates distance and time to travel a given path
def distance_and_time(Graph, origin_coords, destination_coords, path):
    graph_distance = round((path_weight(Graph, path, weight="shape_leng_float") / 3280.8398950131), 2) # convert feet to km
    distance_mi = round((graph_distance * 0.621371), 2) # calculate distance using graph

    # use google maps API to retrieve propietary distance and travel time
    gmaps_distance_matrix = gmaps.distance_matrix(
        origins = (origin_coords[1], origin_coords[0]), 
        destinations = (destination_coords[1], destination_coords[0]),
        mode = "bicycling"
        ) 
    gmaps_distance = float((gmaps_distance_matrix["rows"][0]["elements"][0]["distance"]["text"]).split(" ")[0])
    gmaps_trav_time = float((gmaps_distance_matrix["rows"][0]["elements"][0]["duration"]["text"]).split(" ")[0])
    # approximate travel time using proportionality
    time_min = round(((graph_distance * gmaps_trav_time) / gmaps_distance), 2)
    
    return [distance_mi, time_min] 


def generate_route(origin_address, destination_address):

    road_network = "road_data/nyc_road_data.geojson" # import raw file
    mod_path = "road_data/road_data_bike_mod.geojson" # path of the modified file


    parse_file(signal=True, raw_file=road_network, new_file_name=mod_path) 

    road_network = geopandas.read_file(filename=mod_path) # import mod file

    road_network = arrange_coordinates_direction(file=road_network)
    road_network = geopandas.read_file(filename=mod_path) # re-import updated mod file

    # Create graph
    # Primal graphs represent endpoints as nodes and LineStrings as edges
    # Directed instructs edges to have a direction of travel (e.g. node A is directed to B)
    # MutliGraph allows multiple edges between any pair of nodes, which is a common case in street networks
    # oneway_columns creates an additional edge for each LineString which allows bidirectional path traversal by specifying the boolean column in the GeoDataFrame. If a segment is one-way, then segment's direction must be respected. If it is two-way, segment can be traversed from any direction
    G = momepy.gdf_to_nx(road_network, approach="primal", directed=True, multigraph=True, oneway_column="one_way")

    origin_coords = geocode_closest_node(origin_address, road_network_file=mod_path)[0]
    destination_coords = geocode_closest_node(destination_address, road_network_file=mod_path)[0]

    shortest_path = nx.shortest_path(G, origin_coords, destination_coords, weight="bike_lane_weight")
    
    gdf_path = path_to_gdf(shortest_path)
    route_distance_and_time = distance_and_time(G, origin_coords, destination_coords, shortest_path)

    del G
    
    route_map = create_map(road_network, gdf_path)
    
    return [route_map, route_distance_and_time]
    




    









