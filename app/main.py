from fastapi import FastAPI
from app.database.database import get_db

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, Habit Tracker!"}