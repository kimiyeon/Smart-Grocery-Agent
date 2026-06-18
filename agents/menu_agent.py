from mcp.recipe_mcp import get_recipes

class MenuPlannerAgent:
    def plan(self, context):
        recipes = get_recipes()
        purpose = context["purpose"]

        if purpose == "diet":
            selected = recipes["diet"]
        else:
            selected = recipes["weekly"]

        meals = [meal["menu"] for meal in selected]

        ingredients = []
        for meal in selected:
            ingredients.extend(meal["ingredients"])

        return {
            "meal_plan": meals,
            "ingredients": ingredients
        }