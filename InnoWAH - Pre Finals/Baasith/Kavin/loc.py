import random
import geopandas as gpd
from shapely.geometry import Point
from geopy.distance import geodesic

ocean_shapefile = "ne_110m_ocean"
ocean_gdf = gpd.read_file(ocean_shapefile)

def haversine(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

def is_ocean(lat, lon):
    point = Point(lon, lat)
    return any(ocean_gdf.contains(point))

ships = []
with open("ships.txt", "r", encoding="utf-8") as file:
    for line in file:
        parts = line.strip().split(", ")
        if len(parts) >= 6:
            try:
                lat = float(parts[1].split(": ")[1])
                lon = float(parts[2].split(": ")[1])
                cog = float(parts[4].split(": ")[1].split(" ")[0])
                ships.append((lat, lon, cog))
            except ValueError:
                continue

if not ships:
    exit()

while True:
    random_point = (
        random.uniform(48.5, 51.0),
        random.uniform(-5.0, 2.0)
    )
    
    if is_ocean(random_point[0], random_point[1]):
        nearest_vessels = sorted(
            ships, key=lambda v: haversine(random_point[0], random_point[1], v[0], v[1])
        )
        
        nearest_vessels = [v for v in nearest_vessels if haversine(random_point[0], random_point[1], v[0], v[1]) <= 50]

        if nearest_vessels:
            selected_vessel = random.choice(nearest_vessels)
            break

oil_spill_direction = selected_vessel[2]

output_text = f"Latitude: {random_point[0]}\nLongitude: {random_point[1]}\nOil Spill Direction: {oil_spill_direction+1:.2f}°"

with open("coordinates.txt", 'w', encoding="utf-8") as f:
    f.write(output_text)

print(output_text)
