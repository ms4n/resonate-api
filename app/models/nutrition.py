from sqlalchemy import Column, String, Numeric
from app.db.base import Base


class NutritionData(Base):
    __tablename__ = "nutrition_data"

    food_id = Column(String(100), primary_key=True,
                     unique=True, nullable=False)
    food_name = Column(String(255), nullable=False)
    single_serving_size = Column(Numeric(5, 2), nullable=False)
    quantity = Column(Numeric(5, 2), nullable=False)
    quantity_unit = Column(String(50), nullable=False)
    calories = Column(Numeric(5, 2), nullable=False)
    total_fat = Column(Numeric(5, 2), nullable=False)
    total_carbohydrates = Column(Numeric(5, 2), nullable=False)
    dietary_fiber = Column(Numeric(5, 2), nullable=False)
    protein = Column(Numeric(5, 2), nullable=False)
