from aiogram import Router

from handlers.start import router as start_router
from handlers.monitor_messages import router as messages_router


router = Router()

router.include_router(start_router)
router.include_router(messages_router)
