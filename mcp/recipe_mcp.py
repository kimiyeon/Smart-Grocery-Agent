import json

def get_recipes():
    with open("data/recipes.json", "r") as f:
        return json.load(f)