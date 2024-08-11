from pydantic import BaseModel


class NutritionDataSchema(BaseModel):
    food_id: str
    food_name: str
    single_serving_size: float
    quantity: float
    quantity_unit: str
    calories: float
    total_fat: float
    total_carbohydrates: float
    dietary_fiber: float
    protein: float

    class Config:
        orm_mode = True
