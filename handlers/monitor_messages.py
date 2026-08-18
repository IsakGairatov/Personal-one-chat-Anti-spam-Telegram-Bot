from config import CHAT_ID
from aiogram.types import Message
from aiogram import Router, F
from services.filtration_logic.filter_pymorphy3 import find_spam_word
from services.ai_apis.Gemini_spam_detection import check_spam
from database.queries import get_or_create_user, add_spam_message

router = Router()

@router.message(F.chat.id == CHAT_ID)
async def message_handler(message: Message):
    c_user = await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    if c_user.amount_of_messages <= 100:
        #c_user.amount_of_messages += 1

        has_spam_word = await find_spam_word(message.text)

        if has_spam_word[0] == True:
            await add_spam_message(c_user.id, message.message_id, message.text, has_spam_word[1])



