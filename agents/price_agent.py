from mcp.price_mcp import get_prices

class PriceOptimizerAgent:
    def optimize(self, shopping_items, budget=None):
        prices = get_prices()

        cart = []
        total = 0

        for item in shopping_items:
            price = prices.get(item, 1000)
            total += price
            cart.append({
                "item": item,
                "name": item,
                "price": price
            })

        return {
            "cart": cart,
            "total": total,
            "budget_warning": budget is not None and total > budget
        }