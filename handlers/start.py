from aiogram.filters import CommandStart
from aiogram.types import Message

from database.queries import get_or_create_user

from aiogram import Router

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):

    await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )

    await message.answer("Привет!")