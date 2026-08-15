from datetime import datetime, timedelta

from sqlalchemy import select, func
from database.db import async_session
from database.models import User, SpamMessage


async def create_user(
    telegram_id: int,
    username: str | None,
    first_name: str | None,
) -> User:

    async with async_session() as session:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
        )

        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user

async def get_user(telegram_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        return result.scalar_one_or_none()


async def add_spam_message(
    user_id: int,
    telegram_message_id: int,
    text: str,
) -> SpamMessage:

    async with async_session() as session:
        spam_message = SpamMessage(
            user_id=user_id,
            telegram_message_id=telegram_message_id,
            text=text,
        )

        session.add(spam_message)

        await session.commit()
        await session.refresh(spam_message)

        return spam_message

async def get_spam_count_last_30_days(
    user_id: int,
) -> int:

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    async with async_session() as session:
        result = await session.execute(
            select(func.count(SpamMessage.id))
            .where(
                SpamMessage.user_id == user_id,
                SpamMessage.created_at >= thirty_days_ago,
            )
        )

        return result.scalar_one()

async def ban_user(user_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            return False

        user.is_banned = True

        await session.commit()

        return True