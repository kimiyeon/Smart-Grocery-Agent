POPULAR_KEYWORDS = [
    "chicken", "beef", "pork", "salmon", "fish",
    "pasta", "rice", "fried", "soup", "salad",
    "sandwich", "burger", "pizza", "noodle",
    "curry", "wrap", "sausage", "potato",
    "tomato", "egg", "bread", "fruit",
    "cake", "cookie", "pie", "grilled"
]

UNFAMILIAR_KEYWORDS = [
    "ayam", "percik", "laksa", "rendang",
    "tagine", "koshari", "kedgeree",
    "massaman", "satay", "sambal",
    "cevapi", "burek", "moussaka",
    "shakshuka", "timbits", "goat",
    "kidney", "liver", "offal",
    "arepa", "morcilla", "chorizo",
    "pico", "naan", "plantain", "rocket",
    "algerian", "moroccan", "jamaican",
    "malaysian", "egyptian", "ethiopian"
]

EXOTIC_INGREDIENTS = [
    "sherry", "cardamom", "cumin",
    "oregano", "golden_syrup", "dulce",
    "molasses", "anchovy", "morcilla",
    "chorizo", "naan_bread", "pico_de_gallo",
    "rocket", "fried_ripe_bananas",
    "corn_arepa", "plantain"
]

DESSERT_KEYWORDS = [
    "cake", "cookie", "brownie", "pudding",
    "pie", "tart", "muffin", "dessert",
    "chocolate"
]

PURPOSE_KEYWORDS = {
    "weekly": [
        "rice", "soup", "stew", "chicken", "beef",
        "pasta", "curry", "fried", "noodle", "vegetable"
    ],
    "diet": [
        "salad", "grilled", "chicken", "salmon",
        "fish", "soup", "vegetarian", "vegetable", "tofu"
    ],
    "birthday": [
        "cake", "dessert", "sandwich", "party",
        "fruit", "chocolate", "pasta", "pizza",
        "cookie", "pie", "bread"
    ],
    "camping": [
        "bbq", "barbecue", "grill", "grilled",
        "skewer", "sausage", "pork", "beef",
        "chicken", "rib", "kebab", "potato"
    ]
}


def normalize(text: str) -> str:
    return str(text or "").lower().replace(" ", "_")


def is_dessert_menu(menu: str, ingredients: list[str]) -> bool:
    text = normalize(menu + " " + " ".join(ingredients))

    score = 0

    for keyword in DESSERT_KEYWORDS:
        if keyword in text:
            score += 1

    for keyword in ["flour", "sugar", "butter", "vanilla", "syrup"]:
        if keyword in text:
            score += 1

    return score >= 3


def classify_menu(menu: str, ingredients: list[str], purpose: str = "weekly") -> dict:
    text = normalize(menu + " " + " ".join(ingredients))

    accepted = True
    score = 0
    reasons = []

    for keyword in UNFAMILIAR_KEYWORDS:
        if keyword in text:
            accepted = False
            score -= 10
            reasons.append(f"unfamiliar keyword: {keyword}")

    for keyword in EXOTIC_INGREDIENTS:
        if keyword in text:
            accepted = False
            score -= 10
            reasons.append(f"exotic ingredient: {keyword}")

    if len(ingredients) > 12:
        accepted = False
        score -= 5
        reasons.append("too many ingredients")

    dessert = is_dessert_menu(menu, ingredients)

    if purpose != "birthday" and dessert:
        accepted = False
        score -= 5
        reasons.append("dessert is not suitable for this purpose")

    for keyword in POPULAR_KEYWORDS:
        if keyword in text:
            score += 1

    purpose_keywords = PURPOSE_KEYWORDS.get(purpose, PURPOSE_KEYWORDS["weekly"])

    for keyword in purpose_keywords:
        if keyword in text:
            score += 2

    if accepted and not reasons:
        reasons.append("popular and purpose-compatible menu")

    return {
        "menu": menu,
        "accepted": accepted,
        "score": score,
        "is_dessert": dessert,
        "reasons": reasons,
        "source": "menu-filter-mcp",
    }