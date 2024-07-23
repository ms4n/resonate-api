import os
import time
import json
import hashlib
import psycopg2
import pgvector

from openai import OpenAI
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector

from dotenv import load_dotenv
load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

PGVECTOR_COLLECTION_NAME = os.getenv("PGVECTOR_COLLECTION_NAME")
SIMILARITY_SEARCH_LIMIT = os.getenv("SIMILARITY_SEARCH_LIMIT")

open_ai_client = OpenAI()

EMBEDDINGS_MODEL = "text-embedding-3-small"
INDEX_DIMENSIONS = 1536  # specific for text-embedding-3-small model


# Connect to Supabase Postgresql DB
db_connection = psycopg2.connect(user=POSTGRES_USER,
                                 password=POSTGRES_PASSWORD,
                                 host=POSTGRES_HOST,
                                 port=POSTGRES_PORT,
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

# Convert nutriton data as list of dictionary
nutrition_data_json = [{column_list[i]: data[i]
                        for i in range(len(column_list))} for data in nutrition_data]


def get_embeddings_vector(input_vector_string):
    response = open_ai_client.embeddings.create(
        input=input_vector_string,
        model="text-embedding-3-small"
    )

    print(
        f'Generated embeddings for the string "{input_vector_string}", dimensions: {len(response.data[0].embedding)}')

    return response.data[0].embedding


def get_vector_id(meta):
    food_name = meta.get('food', '')

    # Convert meta dictionary to a JSON string, excluding the 'food' field
    meta_dict = {k: v for k, v in meta.items() if k != 'food'}
    meta_str = json.dumps(meta_dict, sort_keys=True)

    # Generate a hash of the JSON string
    meta_hash = hashlib.sha256(meta_str.encode()).hexdigest()

    # Combine food name with the hash to create the vector ID
    # Use the first 8 characters of the hash for brevity
    vector_id = f'{food_name}-{meta_hash[:8]}'

    print(f'vector_id = {vector_id}')
    return vector_id


def save_vector_and_meta(db_cursor, doc, embedding):
    try:
        vector_id = get_vector_id(doc)
        json_doc = json.dumps(doc)

        query = f"""
            INSERT INTO {PGVECTOR_COLLECTION_NAME} (id, food, embedding, metadata)
            VALUES ('{vector_id}', '{doc["food"]}',
                    '{embedding}', '{json_doc}')
            ON CONFLICT (id)
            DO
                UPDATE SET food = '{doc["food"]}', embedding = '{embedding}', metadata = '{json_doc}'
    """

        db_cursor.execute(query)
        print(f"Vector {vector_id} was added to the DB")

        return vector_id
    except Exception as e:
        print(
            f"[save_vector_and_meta] exception of type {type(e).__name__}: {e}")

# Create and save embeddings for all the records in nutritional data
# for doc in nutrition_data_json:
#     embedding = get_embeddings_vector(doc.get("food"))
#     save_vector_and_meta(db_cursor, doc, embedding)


def get_top_relevant_food_macro_data(db_cursor, food, embeddings, k=5):
    try:
        query = f"""
            WITH vector_matches AS (
                SELECT id, food, metadata, embedding <=> '{embeddings}' AS distance
                FROM {PGVECTOR_COLLECTION_NAME}
            )
            SELECT id, food, metadata, distance
            FROM vector_matches
            ORDER BY distance
            LIMIT '{k}';
        """

        db_cursor.execute(query)
        all_matches = db_cursor.fetchall()

        relevant_matches = []

        print("All matches:")
        for doc in all_matches:
            print(f'-- {round(doc[3], 2)}: {doc[1]} / {doc[2]}')

            # The lower the score value, the more similar vectors are
            if round(doc[3], 2) <= 0.1:
                relevant_matches.append({
                    "document": doc,
                    "score": doc[3]
                })

        if len(relevant_matches) == 0:
            # TODO: Scrape for food macro data, if no data found, add it to db with embeds
            print("No relevant matches found")
        else:
            print("Relevant matches: ")
            [print(f'-- {round(doc["score"], 2)}: {doc["document"][1]} / {doc["document"][2]}')
             for doc in relevant_matches]
        return relevant_matches
    except Exception as e:
        print(f"[get_top_relevant_messages] {type(e).__name__} exception: {e}")
        return []


food_1 = "Chicken"

get_top_relevant_food_macro_data(
    db_cursor, food_1, get_embeddings_vector(food_1.lower()))


db_cursor.close()
db_connection.close()
