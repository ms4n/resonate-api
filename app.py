import os
import json
import psycopg2
import pgvector

from openai import OpenAI
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector

from dotenv import load_dotenv
load_dotenv()


open_ai_client = OpenAI()

# response = open_ai_client.embeddings.create(
#     input="Your text string goes here",
#     model="text-embedding-3-small"
# )

# print(response.data[0].embedding)


# Connect to Postgresql DB and install the pgvector extension
db_connection = psycopg2.connect(user="postgres.axorhmgpwzqruniwisvr",
                                 password=os.getenv("POSTGRES_PASSWORD"),
                                 host="aws-0-ap-south-1.pooler.supabase.com",
                                 port=5432,
                                 dbname="postgres")

db_cursor = db_connection.cursor()
db_connection.autocommit = True


query = """
    SELECT
        food,
        single_serving_size::FLOAT AS single_serving_size,
        calories::FLOAT AS calories,
        total_fat::FLOAT AS total_fat,
        total_carbohydrates::FLOAT AS total_carbohydrates,
        dietary_fiber::FLOAT AS dietary_fiber,
        protein::FLOAT AS protein
    FROM nutrition_data
    """
db_cursor.execute(query)

nutrition_data = db_cursor.fetchall()

column_list = [column[0] for column in db_cursor.description]

nutrition_data_json = [{column_list[i]: data[i]
                        for i in range(len(column_list))} for data in nutrition_data]

db_cursor.close()
db_connection.close()


test_input = nutrition_data_json[0]


