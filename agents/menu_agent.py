from mcp.recipe_mcp import get_recipes

ALLERGY_MAP = {
    "닭고기": ["chicken", "chicken_breast"],
    "치킨": ["chicken", "chicken_breast"],
    "chicken": ["chicken", "chicken_breast"],

    "우유": ["milk", "cheese", "greek_yogurt"],
    "유제품": ["milk", "cheese", "greek_yogurt"],
    "milk": ["milk", "cheese", "greek_yogurt"],
    "dairy": ["milk", "cheese", "greek_yogurt"],

    "계란": ["egg"],
    "달걀": ["egg"],
    "egg": ["egg"],

    "땅콩": ["peanut"],
    "견과류": ["peanut", "almond", "walnut"],
    "peanut": ["peanut"],
    "nuts": ["peanut", "almond", "walnut"],

    "새우": ["shrimp"],
    "해산물": ["shrimp", "fish_cake", "salmon"],
    "seafood": ["shrimp", "fish_cake", "salmon"]
}

class MenuPlannerAgent:
    def plan(self, context):
        recipes = get_recipes()
        purpose = context["purpose"]

        # 목적별 레시피 선택
        selected = recipes.get(purpose, recipes["weekly"])

        # 최대 3개 메뉴 추천
        selected = selected[:3]

        meals = []
        ingredients = []

        for meal in selected:
            meals.append(meal["menu"])
            ingredients.extend(meal["ingredients"])

        return {
            "meal_plan": meals,
            "ingredients": list(dict.fromkeys(ingredients))
        }