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
        food_id,
        food_name,
        single_serving_size::FLOAT AS single_serving_size,
        quantity::FLOAT AS quantity,
        quantity_unit,
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
    input_vector_string = input_vector_string.lower()

    response = open_ai_client.embeddings.create(
        input=input_vector_string,
        model="text-embedding-3-small"
    )

    return response.data[0].embedding


def create_embed_and_save(doc):
    try:
        food_name = doc.get("food_name")
        embedding = get_embeddings_vector(food_name)

        food_id = doc.get("food_id")

        # Convert meta dictionary to a JSON string, excluding the 'food_id' field
        meta_dict = {k: v for k, v in doc.items() if k != 'food_id'}
        meta_str = json.dumps(meta_dict, sort_keys=True)

        # Generate a hash of the JSON string
        meta_hash = hashlib.sha256(meta_str.encode()).hexdigest()

        # Combine food_id with the hash to create the vector ID
        # Use the first 8 characters of the hash for brevity
        vector_id = f'{food_id.lower()}-{meta_hash[:8]}'

        json_doc = json.dumps(doc)

        query = f"""
            INSERT INTO {PGVECTOR_COLLECTION_NAME} (id, food_name, embedding, metadata)
            VALUES ('{vector_id}', '{doc["food_name"]}',
                    '{embedding}', '{json_doc}')
            ON CONFLICT (id)
            DO
                UPDATE SET food_name = '{doc["food_name"]}', embedding = '{embedding}', metadata = '{json_doc}'
        """

        db_cursor.execute(query)
        print(f"Vector {vector_id} was added to the DB")

    except Exception as e:
        print(
            f"[create_embed_and_save] exception of type {type(e).__name__}: {e}")


# for doc in nutrition_data_json:
#     create_embed_and_save(doc)


def get_top_relevant_food_macro_data(db_cursor, food_name, embeddings, k=1):
    query = f"""
            WITH vector_matches AS (
                SELECT id, food_name, metadata, embedding <=> '{embeddings}' AS distance
                FROM {PGVECTOR_COLLECTION_NAME}
            )
            SELECT id, food_name, metadata, distance
            FROM vector_matches
            ORDER BY distance
            LIMIT '{k}';
        """

    try:
        db_cursor.execute(query)
        match = db_cursor.fetchone()

        if match and round(match[3], 2) <= 0.4:
            relevant_match = match[2]
            print(
                f"Relevant match found: {relevant_match} \n Score: {round(match[3], 2)}")
            return relevant_match
        else:
            print("No relevant matches found")
            return None

    except psycopg2.Error as e:
        print(f"Database error in get_top_relevant_food_macro_data: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in get_top_relevant_food_macro_data: {e}")
        return None


def parse_food_input_llm(user_input):
    prompt = f"""
    Parse the following meal description into a list of food items and their quantities.
    Return the result as a JSON array of objects, where each object has 'food', 'quantity', and 'unit' keys.

    User's meal description: {user_input}

    Example output format (in english):
    [
        {{"food": "chicken breast", "quantity": 200, "unit": "g"}},
        {{"food": "brown rice", "quantity": 1, "unit": "cup"}},
        {{"food": "broccoli", "quantity": 100, "unit": "g"}}
    ]

    Output a valid json without any markdown.
    """

    response = open_ai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that parses meal descriptions into structured data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,  # Low temperature for more consistent output
    )

    try:
        parsed_data = json.loads(response.choices[0].message.content)
        return parsed_data
    except json.JSONDecodeError:
        print("Error: LLM response was not valid JSON")
        return []


# Example usage
user_input = "i ate boiled rice with 200g chicken fillet"
parsed_meal = parse_food_input_llm(user_input)


print(json.dumps(parsed_meal, indent=2))

for item in parsed_meal:
    get_top_relevant_food_macro_data(
        db_cursor, item["food"], get_embeddings_vector(item["food"].lower()))


db_cursor.close()
db_connection.close()
