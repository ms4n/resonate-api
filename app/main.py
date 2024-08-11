from fastapi import FastAPI
from app.api.endpoints import nutrition
from app.db.session import engine
from sqlalchemy import text


app = FastAPI()


@app.on_event("startup")
def on_startup():
    # Create the vector extension in PostgreSQL
    with engine.connect() as connection:
        connection.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))


app.include_router(nutrition.router)
