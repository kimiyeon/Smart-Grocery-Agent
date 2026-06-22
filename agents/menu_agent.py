from mcp.recipe_mcp import get_recipes
from mcp.menu_filter_mcp import classify_menu
import random


ALLERGY_MAP = {
    "닭고기": ["chicken", "chicken_breast"],
    "치킨": ["chicken", "chicken_breast"],
    "chicken": ["chicken", "chicken_breast"],

    "우유": ["milk", "cheese", "greek_yogurt", "cream"],
    "유제품": ["milk", "cheese", "greek_yogurt", "cream"],
    "milk": ["milk", "cheese", "greek_yogurt", "cream"],
    "dairy": ["milk", "cheese", "greek_yogurt", "cream"],

    "계란": ["egg", "eggs", "egg_yolk", "egg_yolks"],
    "달걀": ["egg", "eggs", "egg_yolk", "egg_yolks"],
    "egg": ["egg", "eggs", "egg_yolk", "egg_yolks"],

    "땅콩": ["peanut"],
    "견과류": ["peanut", "almond", "walnut", "cashew"],
    "peanut": ["peanut"],
    "nuts": ["peanut", "almond", "walnut", "cashew"],

    "새우": ["shrimp", "prawn"],
    "해산물": ["shrimp", "prawn", "salmon", "fish", "tuna"],
    "seafood": ["shrimp", "prawn", "salmon", "fish", "tuna"],
}


PURPOSE_KEYWORDS = {
    "weekly": [
        "rice", "soup", "stew", "chicken", "beef", "pasta",
        "curry", "fried", "noodle", "vegetable", "potato", "egg"
    ],
    "diet": [
        "salad", "grilled", "chicken", "salmon", "fish", "soup",
        "vegetarian", "vegetable", "bean", "tofu"
    ],
    "birthday": [
        "cake", "dessert", "sandwich", "party", "fruit", "chocolate",
        "pasta", "pizza", "cookie", "pie", "bread"
    ],
    "camping": [
        "bbq", "barbecue", "grill", "grilled", "skewer", "sausage",
        "pork", "beef", "chicken", "rib", "kebab", "potato"
    ],
}


IGNORE_INGREDIENTS = {
    "water",
    "salt",
    "pepper",
    "black_pepper",
    "white_pepper",
    "parsley",
    "bay_leaf",
    "bay_leaves",
    "oregano",
    "thyme",
    "rosemary",
}


EXOTIC_INGREDIENTS = {
    "naan_bread",
    "morcilla",
    "chorizo",
    "pico_de_gallo_sauce",
    "rocket",
    "fried_ripe_bananas",
    "corn_arepa_filled_with_mozarella_cheese",
    "corn_arepa_filled_with_mozzarella_cheese",
    "plantain",
    "plantains",
}


class MenuPlannerAgent:
    def plan(self, context):
        purpose = context.get("purpose", "weekly")
        family_size = context.get("family_size", 1)
        budget = context.get("budget", 50000)

        recipes = get_recipes(purpose)
        blocked = self.get_blocked_items(context.get("allergies", []))
        meal_limit = self.get_meal_limit(family_size, budget)

        safe_recipes = []

        for meal in recipes:
            menu_name = meal.get("menu", "")
            ingredients = meal.get("ingredients", [])

            classification = classify_menu(menu_name, ingredients, purpose)

            if not classification.get("accepted", False):
                continue

            normalized_ingredients = {
                self.normalize_item(item)
                for item in ingredients
            }

            if normalized_ingredients & blocked:
                continue

            score = classification.get("score", 0) + self.score_meal(
                menu_name,
                ingredients,
                purpose
            )

            safe_recipes.append({
                "menu": menu_name,
                "ingredients": ingredients,
                "score": score,
                "is_dessert": classification.get("is_dessert", False),
            })

        # 필터가 너무 강해서 아무 메뉴도 없을 경우:
        # menu-filter-mcp 조건은 무시하고 알레르기만 피해서 fallback 추천
        if not safe_recipes:
            fallback_recipes = []

            for meal in recipes:
                menu_name = meal.get("menu", "")
                ingredients = meal.get("ingredients", [])

                normalized_ingredients = {
                    self.normalize_item(item)
                    for item in ingredients
                }

                if normalized_ingredients & blocked:
                    continue

                fallback_recipes.append({
                    "menu": menu_name,
                    "ingredients": ingredients,
                    "score": self.score_meal(menu_name, ingredients, purpose),
                    "is_dessert": False,
                })

            fallback_recipes.sort(key=lambda x: x["score"], reverse=True)
            safe_recipes = fallback_recipes[:max(meal_limit * 2, meal_limit)]

        if not safe_recipes:
            return {
                "meal_plan": ["추천 가능한 메뉴를 찾지 못했습니다."],
                "ingredients": [],
                "excluded_allergy_items": list(blocked),
                "family_size": family_size,
                "meal_count": 0,
                "quantity_multiplier": self.get_quantity_multiplier(family_size),
            }

        safe_recipes.sort(key=lambda x: x["score"], reverse=True)

        top_pool = safe_recipes[:max(meal_limit * 4, meal_limit)]
        random.shuffle(top_pool)

        selected = []
        dessert_count = 0

        for meal in top_pool:
            if purpose == "birthday" and meal["is_dessert"]:
                if dessert_count >= 1:
                    continue
                dessert_count += 1

            selected.append(meal)

            if len(selected) >= meal_limit:
                break

        if len(selected) < meal_limit:
            for meal in safe_recipes:
                if meal in selected:
                    continue

                if purpose == "birthday" and meal["is_dessert"] and dessert_count >= 1:
                    continue

                selected.append(meal)

                if len(selected) >= meal_limit:
                    break

        selected.sort(key=lambda x: x["score"], reverse=True)

        meals = []
        ingredients = []

        for meal in selected:
            meals.append(meal["menu"])

            for ingredient in meal["ingredients"]:
                normalized = self.normalize_item(ingredient)

                if normalized in IGNORE_INGREDIENTS:
                    continue

                if normalized in EXOTIC_INGREDIENTS:
                    continue

                ingredients.append(normalized)

        return {
            "meal_plan": meals,
            "ingredients": list(dict.fromkeys(ingredients)),
            "excluded_allergy_items": list(blocked),
            "family_size": family_size,
            "meal_count": len(meals),
            "quantity_multiplier": self.get_quantity_multiplier(family_size),
        }

    def normalize_item(self, item):
        return str(item).lower().strip().replace(" ", "_")

    def score_meal(self, menu_name, ingredients, purpose):
        text = self.normalize_item(
            menu_name + " " + " ".join(ingredients)
        )

        keywords = PURPOSE_KEYWORDS.get(
            purpose,
            PURPOSE_KEYWORDS["weekly"]
        )

        score = 0

        for keyword in keywords:
            if keyword in text:
                score += 2

        if purpose == "diet":
            heavy_words = [
                "fried",
                "cake",
                "chocolate",
                "cream",
                "pork",
                "butter"
            ]

            for word in heavy_words:
                if word in text:
                    score -= 2

        if purpose == "birthday":
            if "cake" in text or "cookie" in text or "chocolate" in text:
                score += 2

            if "salad" in text or "soup" in text:
                score -= 1

        if purpose == "camping":
            if "cake" in text or "dessert" in text:
                score -= 3

        return score

    def get_meal_limit(self, family_size, budget):
        if family_size <= 1:
            meal_limit = 1
        elif family_size <= 3:
            meal_limit = 2
        elif family_size <= 5:
            meal_limit = 3
        else:
            meal_limit = 4

        if budget < 30000:
            meal_limit = min(meal_limit, 1)
        elif budget < 50000:
            meal_limit = min(meal_limit, 2)

        return meal_limit

    def get_quantity_multiplier(self, family_size):
        if family_size >= 7:
            return 2.5
        elif family_size >= 5:
            return 2.0
        elif family_size >= 3:
            return 1.5
        return 1.0

    def get_blocked_items(self, allergies):
        blocked = set()

        for allergy in allergies:
            allergy = allergy.strip().lower()

            for key, items in ALLERGY_MAP.items():
                if key.lower() in allergy:
                    blocked.update(
                        self.normalize_item(item)
                        for item in items
                    )

        return blocked