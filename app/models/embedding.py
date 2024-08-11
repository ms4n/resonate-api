from sqlalchemy import Column, String, JSON
from pgvector.sqlalchemy import Vector
from app.db.base import Base


class NutritionDataEmbedding(Base):
    __tablename__ = "nutrition_data_embeddings"

    id = Column(String, primary_key=True)
    food = Column(String)
    metadata = Column(JSON)
    embedding = Column(Vector(1536))
