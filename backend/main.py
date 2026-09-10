from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

class HouseInput(BaseModel):
    area: float
    bedrooms: int
    location: str = "other"

@app.get("/")
def read_root():
    return {"message": "House Price Prediction API"}


def predict_price(area: float, bedrooms: int, location: str) -> float:
    price = 500_000_000
    price += area * 15_000_000
    price += bedrooms * 50_000_000

    location = location.lower()

    if location == "hanoi":
        price *= 1.3
    elif location == "hcmc":
        price *= 1.25

    return round(price / 1_000_000) * 1_000_000


@app.get("/predict")
# Use def because this endpoint only performs synchronous calculations.
def get_prediction(
    area: float,
    bedrooms: int,
    location: str = "other"
):
    predicted_price = predict_price(area, bedrooms, location)

    return {
        "area": area,
        "bedrooms": bedrooms,
        "location": location,
        "predicted_price": predicted_price
    }

@app.post("/predict")
def post_prediction(house: HouseInput):
    predicted_price = predict_price(
        house.area,
        house.bedrooms,
        house.location
    )

    return {
        "area": house.area,
        "bedrooms": house.bedrooms,
        "location": house.location,
        "predicted_price": predicted_price
    }

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)