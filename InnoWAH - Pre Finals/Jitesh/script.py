import websockets
import json
import asyncio
import os
import subprocess

FILE_NAME = "ships.txt"
CONVERT_SCRIPT = "convert.py"

async def connect_ais_stream():
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {
            "APIKey": "8aa7ec30c97b7d033b367478af97f5ec065c52db",
            "BoundingBoxes": [[[36, -9], [52, 1]]],  
            "FilterMessageTypes": ["PositionReport", "ShipStaticData"]  
        }

        await websocket.send(json.dumps(subscribe_message))

        ship_types = {}
        unique_tankers = set()
        count = 0

        async for message_json in websocket:
            message = json.loads(message_json)

            if message["MessageType"] == "ShipStaticData":
                ship_data = message["Message"]["ShipStaticData"]
                mmsi = ship_data.get("UserID", "N/A")
                ship_type_code = ship_data.get("Type", "Unknown")

                if decode_ship_type(ship_type_code) == "Tanker Ship":
                    ship_types[mmsi] = "Tanker Ship"

            elif message["MessageType"] == "PositionReport":
                ais_message = message["Message"]["PositionReport"]
                mmsi = ais_message.get("UserID", "N/A")
                sog = ais_message.get("Sog", 0)

                if sog > 1 and mmsi in ship_types and mmsi not in unique_tankers:
                    unique_tankers.add(mmsi)

                    ship_data = (f"ShipId: {mmsi}, "
                                 f"Latitude: {ais_message.get('Latitude', 'N/A')}, "
                                 f"Longitude: {ais_message.get('Longitude', 'N/A')}, "
                                 f"SOG: {sog} knots, "
                                 f"COG: {ais_message.get('Cog', 'N/A')} degrees, "
                                 f"Ship Type: Tanker Ship")

                    with open(FILE_NAME, "a") as file:
                        file.write(ship_data + "\n")

                    print(ship_data)

                    count += 1
                    if count >= 20:
                        break
    
    run_conversion()

def decode_ship_type(type_code):
    type_map = {
        80: "Tanker Ship"
    }
    return type_map.get(type_code, "Unknown")

def run_conversion():
    if os.path.exists(CONVERT_SCRIPT):
        subprocess.run(["python", CONVERT_SCRIPT], check=True)
    else:
        print(f"Error: {CONVERT_SCRIPT} not found!")

if __name__ == "__main__":
    asyncio.run(connect_ais_stream())