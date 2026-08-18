from config import CHAT_ID, Reply_to_link, Reply_to_spam
import re
from aiogram.types import Message
from aiogram import Router, F
from services.filtration_logic.filter_pymorphy3 import find_spam_word
from services.ai_apis.Gemini_spam_detection import check_spam
from database.queries import get_or_create_user, add_spam_message

router = Router()

@router.message(F.chat.id == CHAT_ID)
async def message_handler(message: Message):
    if not message.text:
        return

    c_user = await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name
    )

    TG_LINK_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/[^\s]+",
        re.IGNORECASE,
    )

    if (TG_LINK_PATTERN.search(message.text)
            or await has_tg_chat_link(message)):
        await message.delete()
        link_reply = await message.answer(Reply_to_link)

        if message.from_user.username:
            await link_reply.reply(f"@{message.from_user.username}")
        return


    if c_user.amount_of_messages <= 100:
        #c_user.amount_of_messages += 1

        has_spam_word = await find_spam_word(message.text)

        if has_spam_word[0] == True:
            if await check_spam(message.text):
                await add_spam_message(c_user.id, message.message_id, message.text, has_spam_word[1])
                try:
                    await message.delete()
                    await message.answer('@' + message.from_user.username + ', ' + Reply_to_spam)

                except:
                    print("Can't delete message")




USERNAME_PATTERN = re.compile(r"(?<!\w)@([a-zA-Z0-9_]{5,32})")


async def has_tg_chat_link(message: Message) -> bool:
    usernames = USERNAME_PATTERN.findall(message.text or "")

    for username in usernames:
        try:
            chat = await message.bot.get_chat(f"@{username}")

            if chat.type in {"group", "supergroup", "channel"}:
                return True

        except Exception:
            continue

    return False