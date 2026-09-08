import asyncio

from config import CHAT_ID, Reply_to_link, Reply_to_spam, Ban_notif
import re
from aiogram.types import Message
from aiogram import Router, F
from services.filtration_logic.filter_pymorphy3 import find_spam_word
from services.ai_apis.Gemini_spam_detection import check_spam
from database.queries import get_or_create_user, add_spam_message, get_spam_count_last_30_days, ban_user, increment_user_messages
from database.models import User

router = Router()

@router.message(F.chat.id == CHAT_ID)
async def message_handler(message: Message):

    if await check_linked_channel(message):
        return

    member = await message.bot.get_chat_member(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
    )

    if member.status in {"creator", "administrator"}:
        return

    text_to_check = message.text or message.caption or ""

    if message.from_user.username:
        us_name = "@" + message.from_user.username
    else:
        us_name = message.from_user.first_name

    c_user = await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name
    )

    if message.reply_markup:
        await message.delete()
        await add_to_spam(c_user, message, text_to_check,"Button", us_name)
        return

    if await basic_tglink_spam_detection(text_to_check, message):
        await add_to_spam(c_user, message, text_to_check, "TG Link", us_name)
        return

    if await full_anti_spam_logic(c_user, text_to_check, message, us_name):
        return

    await increment_user_messages(c_user.id)


TG_LINK_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/[^\s]+",
        re.IGNORECASE,
    )

USERNAME_PATTERN = re.compile(r"(?<!\w)@([a-zA-Z0-9_]{5,32})")


async def full_anti_spam_logic(c_user: User, text_to_check : str, message: Message, us_name: str):
    if c_user.amount_of_messages < 100:

        has_spam_word = await find_spam_word(text_to_check)

        if has_spam_word[0]:
            if await check_spam(text_to_check):
                try:
                    reply_spam = await message.answer(us_name + ', ' + Reply_to_spam)
                    await message.delete()
                    asyncio.create_task(delete_after(reply_spam, 180))
                except:
                    print("delete reply in full_anti_spam_logic error")

                await add_to_spam(c_user, message, text_to_check, has_spam_word[1], us_name)

                return True
    return False

async def add_to_spam(user: User, msg:Message, txt:str, spamword:str, us_name: str, is_guestMode=False):
    if user.amount_of_messages < 100:
        await add_spam_message(user.id, msg.message_id, txt, spamword)
        await check30d(user, msg, us_name)

        if not is_guestMode:
            await punish_guest_caller(txt, msg, spamword)


async def check30d(user:User, msg:Message, us_name):
    if await get_spam_count_last_30_days(user.id) >= 3:
        await msg.bot.ban_chat_member(
            chat_id=msg.chat.id,
            user_id=user.telegram_id
        )
        await ban_user(user.id)
        ban_notif = await msg.answer(us_name + ', ' + Ban_notif)
        asyncio.create_task(delete_after(ban_notif, 180))


async def punish_guest_caller(text_to_check: str, message: Message, spamword):
    bot_caller = message.guest_bot_caller_user
    if bot_caller:
        caller_user = await get_or_create_user(bot_caller.id, bot_caller.username, bot_caller.first_name)

        if bot_caller.username:
            us_name = "@" + bot_caller.username
        else:
            us_name = bot_caller.first_name

        await add_to_spam(caller_user, message, text_to_check, spamword, us_name, True)

async def basic_tglink_spam_detection(text_to_check, message: Message):

    if (TG_LINK_PATTERN.search(text_to_check)
            or await has_tg_chat_link(text_to_check, message)):
        try:
            await message.delete()
            link_reply = await message.answer(Reply_to_link)

            if message.from_user.username:
                link_reply2 = await link_reply.reply(f"@{message.from_user.username}")
                asyncio.create_task(delete_after(link_reply2))
            asyncio.create_task(delete_after(link_reply))
        except:
            print("delete link spam error")

        return True
    return False

async def has_tg_chat_link(text_to_check: str, message: Message) -> bool:
    usernames = USERNAME_PATTERN.findall(text_to_check or "")

    for username in usernames:
        try:
            chat = await message.bot.get_chat(f"@{username}")

            if chat.type in {"group", "supergroup", "channel"}:
                return True

        except Exception:
            continue

    return False

async def check_linked_channel(message: Message):
    chat = await message.bot.get_chat(message.chat.id)

    if (
            message.sender_chat
            and message.sender_chat.type == "channel"
            and message.sender_chat.id == chat.linked_chat_id
    ): return True

    return False

async def delete_after(message: Message, seconds: int = 60):
    await asyncio.sleep(seconds)
    try:
        await message.delete()
    except:
        print("delete_after error")