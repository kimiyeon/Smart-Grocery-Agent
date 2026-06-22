from agents.context_agent import ContextAgent
from agents.menu_agent import MenuPlannerAgent
from agents.inventory_agent import InventoryFilterAgent
from agents.price_agent import PriceOptimizerAgent
from mcp.price_mcp import get_prices

class MasterAgent:
    def __init__(self):
        self.context_agent = ContextAgent()
        self.menu_agent = MenuPlannerAgent()
        self.inventory_agent = InventoryFilterAgent()
        self.price_agent = PriceOptimizerAgent()

    def run(self, user_input):
        context = self.context_agent.analyze(user_input)

        recipes_context = self.menu_agent.plan(context)
        candidate_meals = recipes_context["meal_plan"]

        # 다시 recipe data에서 메뉴별 재료 매핑 가져오기
        from mcp.recipe_mcp import get_recipes
        recipes = get_recipes()
        purpose = context["purpose"]
        selected_pool = recipes.get(purpose, recipes["weekly"])

        prices = get_prices()

        final_meals = []
        final_ingredients = []
        total = 0

        for meal in selected_pool:
            meal_ingredients = meal["ingredients"]

            # 냉장고 재고 제거 후 가격 계산
            filtered = self.inventory_agent.filter(meal_ingredients)
            meal_cost = sum(prices.get(item, 1000) for item in filtered)

            # 예산 안에 들어오면 메뉴 전체를 추가
            if total + meal_cost <= context["budget"]:
                final_meals.append(meal["menu"])
                final_ingredients.extend(filtered)
                total += meal_cost

            if len(final_meals) >= 3:
                break

        # 예산이 너무 낮아서 아무 메뉴도 못 고르면 가장 싼 메뉴 하나는 넣기
        if not final_meals and selected_pool:
            cheapest = min(
                selected_pool,
                key=lambda meal: sum(
                    prices.get(item, 1000)
                    for item in self.inventory_agent.filter(meal["ingredients"])
                )
            )
            final_meals.append(cheapest["menu"])
            final_ingredients.extend(self.inventory_agent.filter(cheapest["ingredients"]))

        final_ingredients = list(dict.fromkeys(final_ingredients))
        result = self.price_agent.optimize(final_ingredients, context["budget"])

        return {
            "context": context,
            "meal_plan": final_meals,
            "shopping_list": result["cart"],
            "total_cost": result["total"],
            "budget": context["budget"],
            "budget_warning": result.get("budget_warning", False)
        }