from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from test_model import run

import psycopg2
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

def connect_to_db(settings):
  try:
    connection = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password
    )
    return connection
  except Exception as error:
    print(f"Error while connecting to PostgreSQL: {error}")
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

load_dotenv('.env.local')

class Settings(BaseSettings):
    db_host: str = ""
    db_port: int = 5432
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""

settings = Settings()

connection = connect_to_db(settings)

@app.get("/cards/{card_id}")
async def read_card(card_id):
    try:
        results = run(card_id, connection)
        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while classifying.")
