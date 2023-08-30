from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from test_model import classify

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

@app.get("/cards/{card_id}")
async def read_card(card_id):
    try:
        results = classify(card_id)
        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while classifying.")
