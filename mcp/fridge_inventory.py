import json

def get_fridge_items():
    with open("data/fridge.json", "r") as f:
        data = json.load(f)
    return data["items"]