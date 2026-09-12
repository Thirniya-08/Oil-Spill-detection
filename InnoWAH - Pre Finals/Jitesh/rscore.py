import math
import datetime

FILE_NAME = "ships.txt"

def get_user_input():
    lat = float(input("Enter oil spill latitude: "))
    lon = float(input("Enter oil spill longitude: "))
    spill_direction = float(input("Enter spill direction (in degrees): "))
    return lat, lon, spill_direction

def read_ship_data():
    unique_tankers = []
    seen_ships = set()

    with open(FILE_NAME, "r") as file:
        for line in file:
            match = line.strip().split(", ")
            if len(match) >= 6:
                ship_id = match[0].split(": ")[1]
                latitude = float(match[1].split(": ")[1])
                longitude = float(match[2].split(": ")[1])
                sog = float(match[3].split(": ")[1].split(" ")[0])
                cog = float(match[4].split(": ")[1].replace(" degrees", ""))  
                ship_type = match[5].split(": ")[1]

                if ship_type == "Tanker Ship" and ship_id not in seen_ships:
                    unique_tankers.append({
                        "id": ship_id,
                        "latitude": latitude,
                        "longitude": longitude,
                        "sog": sog,
                        "cog": cog,
                        "timestamp": datetime.datetime.now(datetime.UTC)
                    })
                    seen_ships.add(ship_id)

                    if len(unique_tankers) == 20:
                        break

    return unique_tankers

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  

def calculate_heading_difference(ship_cog, spill_direction):
    delta_theta = abs(ship_cog - spill_direction) % 360
    return min(delta_theta, 360 - delta_theta)  

def calculate_r_score(ship, spill_lat, spill_lon, spill_direction, spill_time):
    distance = haversine(ship["latitude"], ship["longitude"], spill_lat, spill_lon)
    delta_h = max(0.1, (spill_time - ship["timestamp"]).total_seconds() / 3600)  
    delta_theta = calculate_heading_difference(ship["cog"], spill_direction)
    
    if delta_theta >= 45:
        return 0  

    return (1 - (delta_theta / 45)) * (1 / delta_h)

def main():
    spill_lat, spill_lon, spill_direction = get_user_input()
    spill_time = datetime.datetime.now(datetime.UTC)
    ships = read_ship_data()
    results = []

    for ship in ships:
        r_score = calculate_r_score(ship, spill_lat, spill_lon, spill_direction, spill_time)
        if r_score > 0:
            results.append((ship["id"], r_score))

    results.sort(key=lambda x: x[1], reverse=True)

    for ship_id, score in results:
        print(f"Ship ID: {ship_id}, R-Score: {score:.4f}")

if __name__ == "__main__":
    main()
