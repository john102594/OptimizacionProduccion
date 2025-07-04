import json
import os

SETUP_TIMES = {}
try:
    json_file_path = os.path.join(os.path.dirname(__file__), "..", "setup_times.json")
    with open(json_file_path, "r") as f:
        SETUP_TIMES = json.load(f)
except FileNotFoundError:
    print("setup_times.json not found. Setup times will not be applied.")
except json.JSONDecodeError:
    print("Error decoding setup_times.json. Setup times will not be applied.")

def get_setup_time(from_type, to_type):
    if not SETUP_TIMES:
        return 0.0
    if from_type is None:
        return 0.0
    return SETUP_TIMES.get(from_type, {}).get(to_type, 0.0)