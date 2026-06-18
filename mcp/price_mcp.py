import json

def get_prices():
    with open("data/prices.json", "r") as f:
        return json.load(f)