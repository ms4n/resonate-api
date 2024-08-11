from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.nutrition import NutritionDataSchema
from app.services.nutrition_service import process_nutrition_data
from app.services import nutrition_service
from app.db.session import get_db

router = APIRouter()


@router.get("/nutrition/{food_name}", response_model=NutritionDataSchema)
async def get_nutrition_data(food_name: str, db: Session = Depends(get_db)):
    return nutrition_service.process_nutrition_data(db, food_name)
