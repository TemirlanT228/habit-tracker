from fastapi import FastAPI
from app.routers import habits, user

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, Habit Tracker!"}

app.include_router(user.router)
app.include_router(habits.router)