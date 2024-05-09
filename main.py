from flask import Flask, render_template, request
import geopandas

from scripts.main_b_mod import *


app = Flask(__name__)

@app.route("/", methods=('GET', 'POST'))
def root():
    
    # GET method / default map
    default_map = geopandas.read_file(filename="road_data/default_map_nyc.geojson")
    default_map = default_map.explore()
    default_map = default_map._repr_html_()

    if request.method == 'POST':
        origin_address = request.form['origin']
        destination_address = request.form['destination']
        route = generate_route(origin_address, destination_address) 
        return render_template("index.html", 
                               route_map=route[0], 
                               route_distance_and_time=route[1], 
                               origin_address=origin_address, 
                               destination_address=destination_address)
        
    # GET return
    return render_template("index.html", route_map=default_map)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)