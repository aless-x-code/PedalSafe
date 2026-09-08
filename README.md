# 🚲 PedalSafe Route Planner 🚲 

PedalSafe Route Planner is a web app designed to calculate and visualize the _safest_ bike routes between two locations in New York City. It factors distance, and cycling lanes level of protection, resulting in the safest and shortest way of getting from point A to B.  

![PedalSafe Route Planner](https://i.imgur.com/LuOaPRU.jpeg)

## Features
- **Dynamic Route Calculation:** Input an origin and destination to receive the optimal bike route, considering bike lane hierarchy, travel distance, and road network directionality.
- **Visualization:** View the route on an interactive map with overlays for bike lanes and road networks.
- **Distance and Time Estimates:** Get estimated distance and travel time for the bike route.

## Tools & Technologies Used
- 🌶️ **Flask:** Web framework for handling HTTP requests and rendering templates.
- 🐼 **Geopandas:** For reading and manipulating geospatial data.
- 🕸️ **NetworkX:** For graph generation and route calculations.
- ⚙️ **Momepy:** For converting GeoDataFrames to NetworkX graphs.
- 🗺️ **Folium:** For map visualization.
- 🧭 **Google Maps API:** For geocoding addresses and estimating travel times.

## Installation
1. Set up enviorment:
```
git clone https://github.com/aless-x-code/PedalSafe.git
cd pedalsafe
```
```
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
```
pip install -r requirements.txt
```

2. Set up Google Maps API Key:

Ensure you have a Google Maps API key and save it in a file named scripts/keys.py:

```python
def get_key():
    return 'YOUR_GOOGLE_MAPS_API_KEY'
```

## Usage
1. Local deployment:
```
python main.py
```
2. Access the local server:

Open a web browser and navigate to http://127.0.0.1:8080.

3. Interact with the application:

- **Homepage:** By default, the application shows a default map of NYC, along with route inputs.
- **Calculate Route:** Enter the origin and destination addresses in the form to calculate and visualize the bike route.

## File Structure
```
pedalsafe
│   README.md
│   requirements.txt  
│   main.py
│   .gitignore
│
└───templates
│   │   index.html
│   
└───static
│   │   script.js
│   │   style.css
│   
└───scripts
│   │   keys.py
│   │   main_b_mod.py
│   
└───road_data
│   │   default_map_nyc.geojson
│   │   nyc_road_data.geojson
│   │   road_data_bike_mod.geojson
│   │   roads_bike_mod.geojson
```
- **main.py:** Main Flask application file.
- **requirements.txt:** List of required Python packages.
- **scripts/main_b_mod.py:** Contains functions for processing bike lane data, calculating routes, and generating maps.
- **scripts/keys.py:** Stores Google Maps API key.

