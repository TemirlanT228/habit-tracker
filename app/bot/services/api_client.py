from typing import List, Optional
import httpx
from app.bot.schemas.user import UserCreate, UserResponse
from app.bot.schemas.habit import HabitCreate, HabitResponse

class ApiClient:
    def __init__(self, base_url: str = "http://backend:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(follow_redirects=True)

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserResponse]:
        response = await self.client.get(
            f"{self.base_url}/users/",
            params={"telegram_id": telegram_id}
        )
        response.raise_for_status()
        users = response.json()
        if users:
            return UserResponse(**users[0])
        return None

    async def create_user(self, telegram_id: int, username: Optional[str]) -> UserResponse:
        user = UserCreate(telegram_id=telegram_id, username=username)
        response = await self.client.post(
            f"{self.base_url}/users/", 
            json=user.model_dump()
        )
        response.raise_for_status()
        return UserResponse(**response.json())

    async def create_habit(self, habit: HabitCreate) -> HabitResponse:
        response = await self.client.post(
            f"{self.base_url}/habits/",  
            json=habit.model_dump()
        )
        response.raise_for_status()
        return HabitResponse(**response.json())

    async def get_habits(self, telegram_id: int) -> List[HabitResponse]:
        response = await self.client.get(
            f"{self.base_url}/habits/",  
            params={"telegram_id": telegram_id}
        )
        response.raise_for_status()
        return [HabitResponse(**habit) for habit in response.json()]
    
    async def update_habit(self, habit_id: int, user_id: int, updates: dict) -> HabitResponse:
        response = await self.client.patch(
            f"{self.base_url}/habits/{habit_id}",
            params={"user_id": user_id},
            json=updates
        )
        response.raise_for_status()
        return HabitResponse(**response.json())

    async def close(self):
        await self.client.aclose()