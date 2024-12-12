import json
from pathlib import Path

# Upload codes identifying airlines and airports and api keys
try:
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"

    # Load JSON files from the 'data' directory
    with open(DATA_DIR/"airline_codes.json", "r") as json_file:
        airline_codes = json.load(json_file)

    with open(DATA_DIR/"iata_codes.json", "r") as json_file:
        iata_codes = json.load(json_file)

    with open(DATA_DIR/"api_key.json", "r") as json_file:
        api_key = json.load(json_file)    

except FileNotFoundError as e:
    print("Make sure that 'airline_codes.json', 'iata_codes.json' and 'api_keys.json' are present.")