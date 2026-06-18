from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agents.master_agent import MasterAgent
from agents.context_agent import ContextAgent
from agents.menu_agent import MenuPlannerAgent
from agents.inventory_agent import InventoryFilterAgent
from agents.price_agent import PriceOptimizerAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

context_agent = ContextAgent()
menu_agent = MenuPlannerAgent()
inventory_agent = InventoryFilterAgent()
price_agent = PriceOptimizerAgent()


class UserInput(BaseModel):
    family: list
    allergies: list
    purpose: str
    budget: int


@app.get("/")
def home():
    return {"message": "Smart Grocery Agent Running"}


@app.post("/generate-shopping-list")
def generate(data: UserInput):
    result = master_agent.run(data.model_dump())
    return result