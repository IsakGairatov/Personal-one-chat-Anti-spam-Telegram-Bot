import asyncio

from config import CHAT_ID, Reply_to_link, Reply_to_spam, Ban_notif
import re
from aiogram.types import Message
from aiogram import Router, F
from services.filtration_logic.filter_pymorphy3 import find_spam_word
from services.ai_apis.Gemini_spam_detection import check_spam
from database.queries import get_or_create_user, add_spam_message, get_spam_count_last_30_days, ban_user

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
            link_reply2 = await link_reply.reply(f"@{message.from_user.username}")
            await delete_after(link_reply2)
        await delete_after(link_reply)

        return


    if c_user.amount_of_messages <= 100:
        c_user.amount_of_messages += 1

        has_spam_word = await find_spam_word(message.text)

        if has_spam_word[0] == True:
            if await check_spam(message.text):
                await add_spam_message(c_user.id, message.message_id, message.text, has_spam_word[1])

                if message.from_user.username: us_name = "@" + message.from_user.username
                else: us_name = message.from_user.first_name

                try:
                    await message.delete()
                    reply_spam = await message.answer(us_name + ', ' + Reply_to_spam)
                    await delete_after(reply_spam, 180)

                except:
                    print("Error")

                spam_count = await get_spam_count_last_30_days(message.from_user.id)

                print("Telegram ID:", message.from_user.id)
                print("Spam count:", spam_count)

                if spam_count >= 3:
                    print("БАНИМ")
                    await message.bot.ban_chat_member(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id
                    )

                if await get_spam_count_last_30_days(message.from_user.id) >= 3:
                    await message.bot.ban_chat_member(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id
                    )
                    await ban_user(message.from_user.id)
                    ban_notif = await message.answer(us_name + ', ' + Ban_notif)
                    await delete_after(ban_notif, 180)




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

async def delete_after(message: Message, seconds: int = 60):
    await asyncio.sleep(seconds)
    await message.delete()