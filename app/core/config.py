import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    SIMILARITY_SEARCH_LIMIT: float = float(
        os.getenv("SIMILARITY_SEARCH_LIMIT", 0.4))


settings = Settings()
