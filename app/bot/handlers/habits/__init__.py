from aiogram import Router
from .create import *
from .list import *
from .edit import *
from .common import *

router = Router()

# Зарегистрировать все хэндлеры в habits.router
from .create import router as create_router
from .list import router as list_router
from .edit import router as edit_router
from .common import router as common_router

router.include_router(create_router)
router.include_router(list_router)
router.include_router(edit_router)
router.include_router(common_router)
