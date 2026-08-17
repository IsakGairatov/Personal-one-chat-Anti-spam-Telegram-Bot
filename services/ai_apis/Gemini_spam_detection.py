import asyncio
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_ANTI_SPAM_API_KEY")
)


SYSTEM_PROMPT = """Ты — антиспам-модератор Telegram-чата.

Определи, является ли сообщение спамом.

Спамом считаются:
- реклама;
- навязчивое продвижение товаров или услуг;
- подозрительные ссылки;
- мошеннические предложения;
- массовые рекламные сообщения;
- предложения заработать деньги;
- сообщения, явно направленные на привлечение пользователей куда-либо.

Обычный разговор пользователей спамом НЕ является.

Оцени вероятность того, что сообщение является спамом, числом от 0.0 до 1.0.

Ответь кратко только числом.
"""


async def check_spam(text: str) -> bool:
    response = await client.aio.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=SYSTEM_PROMPT + f"\n\nСообщение:\n{text}",
        config=types.GenerateContentConfig(
        )
    )

    return float(response.text.strip()) > 0.75



