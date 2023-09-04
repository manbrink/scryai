import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from test_model import run

import psycopg2
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from time import sleep

BASEDIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASEDIR, '.env.local'))

class Settings(BaseSettings):
    db_host: str = ""
    db_port: int = 5432
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""

settings = Settings()

def connect_to_db(retries=5):
    print("Connecting to PostgreSQL...")

    for _ in range(retries):
        try:
            connection = psycopg2.connect(
                host=settings.db_host,
                port=settings.db_port,
                dbname=settings.db_name,
                user=settings.db_user,
                password=settings.db_password
            )
            print("Connected to PostgreSQL.")
            return connection
        except Exception as error:
            print(f"Error while connecting to PostgreSQL: {error}")
            sleep(3)
    return None

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("main.py body...")

@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    global connection
    connection = connect_to_db()
    print("Startup complete.")

@app.get("/cards/{card_id}")
async def read_card(card_id):
    try:
        print(f"Received request for card {card_id}")
        results = run(card_id, connection)
        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while classifying.")
