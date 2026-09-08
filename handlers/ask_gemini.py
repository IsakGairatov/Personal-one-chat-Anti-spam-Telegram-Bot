from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from config import CHAT_ID

from services.ai_apis.Gemini_googling import ask_ai

router = Router()

@router.message(Command("ask"), F.chat.id == CHAT_ID)
async def ask_handler(message: Message):
    parts = message.text.split(maxsplit=1)
    question = parts[1].strip() if len(parts) > 1 else ""

    if not question:
        await message.reply("Напиши вопрос после /ask")
        return

    # Сначала отправляем сообщение о начале обработки
    processing_message = await message.reply("Запрос в обработке...")

    try:
        answer = await ask_ai(question)
        await processing_message.delete()
        await message.reply(answer)

    except Exception:
        await processing_message.delete()

        await message.reply(
            "Не удалось получить ответ. Попробуй ещё раз."
        )