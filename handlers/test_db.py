import asyncio

from database.db import create_tables
from database.queries import (
    create_user,
    get_user,
    add_spam_message,
    get_spam_count_last_30_days,
    ban_user,
)


async def main():
    # 1. Создаём таблицы
    await create_tables()

    print("\n--- CREATE USER ---")

    user = await create_user(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
    )

    print("ID:", user.id)
    print("Telegram ID:", user.telegram_id)
    print("Username:", user.username)
    print("Banned:", user.is_banned)

    # 2. Получаем пользователя
    print("\n--- GET USER ---")

    found_user = await get_user(123456789)

    print("Found:", found_user)
    print("Username:", found_user.username if found_user else None)


    # 4. Добавляем три спам-сообщения
    print("\n--- ADD SPAM ---")

    for i in range(3):
        spam = await add_spam_message(
            user_id=user.id,
            telegram_message_id=100 + i,
            text=f"Spam message {i + 1}",
        )

        print(
            "Spam ID:",
            spam.id,
            "| Text:",
            spam.text,
        )

    # 5. Считаем спам за 30 дней
    print("\n--- SPAM COUNT ---")

    count = await get_spam_count_last_30_days(
        user.id
    )

    print("Spam count:", count)

    # 6. Баним пользователя
    print("\n--- BAN USER ---")

    if count >= 3:
        await ban_user(user.id)


if __name__ == "__main__":
    asyncio.run(main())