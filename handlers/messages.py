import os
from config import CHAT_ID
from aiogram.types import Message
from aiogram import Router, F

router = Router()

@router.message(F.chat.id == CHAT_ID)
async def message_handler(message: Message):
    print(message.text)
