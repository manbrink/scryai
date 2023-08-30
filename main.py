from fastapi import FastAPI
from test_model import classify

app = FastAPI()


@app.get("/cards/{card_id}")
async def read_card(card_id):
    results = classify(card_id)

    return {"results": results}
