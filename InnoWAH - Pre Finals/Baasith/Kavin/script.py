import websockets
import json
import asyncio
import os

FILE_NAME = "ships.txt"

async def connect_ais_stream():
    # Delete existing file if it exists
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {
            "APIKey": "8aa7ec30c97b7d033b367478af97f5ec065c52db",
            "BoundingBoxes": [[[36, -9], [52, 1]]],  
            "FilterMessageTypes": ["PositionReport", "ShipStaticData"]  
        }

        await websocket.send(json.dumps(subscribe_message))

        ship_types = {}  # Store MMSI -> Ship Type mapping
        unique_tankers = set()
        count = 0

        async for message_json in websocket:
            message = json.loads(message_json)

            # Store Ship Type from ShipStaticData
            if message["MessageType"] == "ShipStaticData":
                ship_data = message["Message"]["ShipStaticData"]
                mmsi = ship_data.get("UserID", "N/A")
                ship_type_code = ship_data.get("Type", "Unknown")

                # Store only if the ship is an oil tanker
                if decode_ship_type(ship_type_code) == "Tanker Ship":
                    ship_types[mmsi] = "Tanker Ship"

            # Process Position Reports
            elif message["MessageType"] == "PositionReport":
                ais_message = message["Message"]["PositionReport"]
                mmsi = ais_message.get("UserID", "N/A")  # Unique ship ID
                sog = ais_message.get("Sog", 0)  # Speed Over Ground

                if sog > 1 and mmsi in ship_types and mmsi not in unique_tankers:  # Only moving oil tankers
                    unique_tankers.add(mmsi)

                    ship_data = (f"ShipId: {mmsi}, "
                                 f"Latitude: {ais_message.get('Latitude', 'N/A')}, "
                                 f"Longitude: {ais_message.get('Longitude', 'N/A')}, "
                                 f"SOG: {sog} knots, "
                                 f"COG: {ais_message.get('Cog', 'N/A')} degrees, "
                                 f"Ship Type: Tanker Ship")

                    # Save to file
                    with open(FILE_NAME, "a") as file:
                        file.write(ship_data + "\n")

                    print(ship_data)  # Print to console

                    count += 1
                    if count >= 20:
                        break  # Stop after 20 unique oil tankers

def decode_ship_type(type_code):
    """ Maps AIS ship type codes to vessel categories """
    type_map = {
        80: "Tanker Ship"  # Oil Tankers
    }
    return type_map.get(type_code, "Unknown")

if __name__ == "__main__":
    asyncio.run(connect_ais_stream())
