import json
import re

# Input and output file paths
input_file = "ships.txt"
output_file = "ais_data.json"

def convert_to_json(input_file, output_file):
    """Convert ships.txt to ais_data.json."""
    ships = []
    pattern = re.compile(
        r"ShipId: (\d+), Latitude: ([\d.-]+), Longitude: ([\d.-]+), SOG: ([\d.]+) knots, COG: ([\d.]+) degrees, Ship Type: (.+)"
    )

    # Read ships.txt and parse data
    with open(input_file, "r") as file:
        for line in file:
            match = pattern.match(line.strip())
            if match:
                ship = {
                    "ShipId": match.group(1),
                    "Latitude": float(match.group(2)),
                    "Longitude": float(match.group(3)),
                    "SOG": float(match.group(4)),
                    "COG": float(match.group(5)),
                    "Type": match.group(6),
                }
                ships.append(ship)

    # Write data to ais_data.json
    with open(output_file, "w") as file:
        json.dump(ships, file, indent=4)

    print(f"Converted {input_file} to {output_file} successfully!")

# Run the conversion
convert_to_json(input_file, output_file)
