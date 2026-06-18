from mcp.fridge_inventory import get_fridge_items

class InventoryFilterAgent:
    def filter(self, ingredients):
        fridge = get_fridge_items()
        remaining = [item for item in ingredients if item not in fridge]
        return remaining