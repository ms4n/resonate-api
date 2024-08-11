from sqlalchemy.orm import Session
from app.crud.nutrition import get_nutrition_data_by_food_name
from app.schemas.nutrition import NutritionDataSchema


def process_nutrition_data(db: Session, food_name: str) -> NutritionDataSchema:
    nutrition_data = get_nutrition_data_by_food_name(db, food_name)
    if not nutrition_data:
        raise ValueError("Nutrition data not found.")

    return nutrition_data
