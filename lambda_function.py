import os
import psycopg2
from time import sleep
import json

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

        # print("Received event: " + str(event))

        card_id = event['pathParameters']['card_id'] if 'card_id' in event['pathParameters'] else ''

        # print("Card ID: " + card_id)

        results = run(card_id, connection)

        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(results) if results else json.dumps([])
        }
    except Exception as e:
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": str(e)
        }