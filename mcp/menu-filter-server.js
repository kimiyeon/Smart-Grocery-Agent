import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  {
    name: "menu-filter-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const POPULAR_KEYWORDS = [
  "chicken", "beef", "pork", "salmon", "fish",
  "pasta", "rice", "fried", "soup", "salad",
  "sandwich", "burger", "pizza", "noodle",
  "curry", "wrap", "sausage", "potato",
  "tomato", "egg", "bread", "fruit",
  "cake", "cookie", "pie", "grilled"
];

const UNFAMILIAR_KEYWORDS = [
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
];

const EXOTIC_INGREDIENTS = [
  "sherry", "cardamom", "cumin",
  "oregano", "golden_syrup", "dulce",
  "molasses", "anchovy", "morcilla",
  "chorizo", "naan_bread", "pico_de_gallo",
  "rocket", "fried_ripe_bananas",
  "corn_arepa", "plantain"
];

const DESSERT_KEYWORDS = [
  "cake", "cookie", "brownie", "pudding",
  "pie", "tart", "muffin", "dessert",
  "chocolate"
];

const PURPOSE_KEYWORDS = {
  weekly: [
    "rice", "soup", "stew", "chicken", "beef",
    "pasta", "curry", "fried", "noodle", "vegetable"
  ],
  diet: [
    "salad", "grilled", "chicken", "salmon",
    "fish", "soup", "vegetarian", "vegetable", "tofu"
  ],
  birthday: [
    "cake", "dessert", "sandwich", "party",
    "fruit", "chocolate", "pasta", "pizza",
    "cookie", "pie", "bread"
  ],
  camping: [
    "bbq", "barbecue", "grill", "grilled",
    "skewer", "sausage", "pork", "beef",
    "chicken", "rib", "kebab", "potato"
  ]
};

function normalize(text) {
  return String(text || "").toLowerCase().replaceAll(" ", "_");
}

function isDessert(text) {
  let score = 0;

  for (const word of DESSERT_KEYWORDS) {
    if (text.includes(word)) score += 1;
  }

  for (const word of ["flour", "sugar", "butter", "vanilla", "syrup"]) {
    if (text.includes(word)) score += 1;
  }

  return score >= 3;
}

function classifyMenu(menu, ingredients, purpose) {
  const normalizedText = normalize(menu + " " + ingredients.join(" "));

  const reasons = [];
  let score = 0;
  let accepted = true;

  for (const word of UNFAMILIAR_KEYWORDS) {
    if (normalizedText.includes(word)) {
      accepted = false;
      reasons.push(`unfamiliar keyword: ${word}`);
      score -= 10;
    }
  }

  for (const word of EXOTIC_INGREDIENTS) {
    if (normalizedText.includes(word)) {
      accepted = false;
      reasons.push(`exotic ingredient: ${word}`);
      score -= 10;
    }
  }

  if (ingredients.length > 12) {
    accepted = false;
    reasons.push("too many ingredients");
    score -= 5;
  }

  const dessert = isDessert(normalizedText);

  if (purpose !== "birthday" && dessert) {
    accepted = false;
    reasons.push("dessert is not suitable for this purpose");
    score -= 5;
  }

  for (const word of POPULAR_KEYWORDS) {
    if (normalizedText.includes(word)) {
      score += 1;
    }
  }

  const purposeWords = PURPOSE_KEYWORDS[purpose] || PURPOSE_KEYWORDS.weekly;

  for (const word of purposeWords) {
    if (normalizedText.includes(word)) {
      score += 2;
    }
  }

  if (accepted && reasons.length === 0) {
    reasons.push("popular and purpose-compatible menu");
  }

  return {
    menu,
    accepted,
    score,
    is_dessert: dessert,
    reasons,
    source: "menu-filter-mcp",
  };
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "classify_menu",
        description:
          "Classify whether a meal is familiar and suitable for the shopping purpose.",
        inputSchema: {
          type: "object",
          properties: {
            menu: {
              type: "string",
              description: "Meal name",
            },
            ingredients: {
              type: "array",
              items: { type: "string" },
              description: "Ingredient list",
            },
            purpose: {
              type: "string",
              description: "weekly, diet, birthday, or camping",
            },
          },
          required: ["menu", "ingredients", "purpose"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "classify_menu") {
    const result = classifyMenu(
      args.menu,
      args.ingredients || [],
      args.purpose || "weekly"
    );

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result),
        },
      ],
    };
  }

  throw new Error("Unknown tool");
});

const transport = new StdioServerTransport();
await server.connect(transport);