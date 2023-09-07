import os
import psycopg2
from time import sleep

from test_model import run

def connect_to_db(retries=5):
    print("Connecting to PostgreSQL...")

    for _ in range(retries):
        try:
            connection = psycopg2.connect(
                host=os.environ.get("DB_HOST"),
                port=os.environ.get("DB_PORT"),
                dbname=os.environ.get("DB_NAME"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD"),
            )
            print("Connected to PostgreSQL.")
            return connection
        except Exception as error:
            print(f"Error while connecting to PostgreSQL: {error}")
            sleep(3)
    return None

def lambda_handler(event, context):
    try:
        connection = connect_to_db()

        card_id = event['card_id']

        results = run(card_id, connection)

        response = {
            "isBase64Encoded": False,
            "statusCode": 200,
            "body": results,
            "headers": {
                "content-type": "application/json"
            }
        }

        return response
    except Exception as e:
        response = {
            "isBase64Encoded": False,
            "statusCode": 500,
            "body": str(e),
            "headers": {
                "content-type": "application/json"
            }
        }

        return response