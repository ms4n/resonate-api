from sqlalchemy.orm import Session
from app.models.nutrition import NutritionData


def get_nutrition_data_by_food_name(db: Session, food_id: str):
    return db.query(NutritionData).filter(NutritionData.food_id == food_id).first()


def create_nutrition_data(db: Session, nutrition_data: NutritionData):
    db.add(nutrition_data)
    db.commit()
    db.refresh(nutrition_data)
    return nutrition_data
