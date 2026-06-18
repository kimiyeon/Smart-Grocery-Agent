def recommend_store(total_cost):
    if total_cost > 50000:
        return "Wholesale Mart"
    return "Local Grocery"