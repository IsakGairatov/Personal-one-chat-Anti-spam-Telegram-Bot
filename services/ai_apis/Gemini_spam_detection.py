import asyncio
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from config import GEMINI_ANTI_SPAM_API_KEY


load_dotenv()

client = genai.Client(
    api_key=GEMINI_ANTI_SPAM_API_KEY
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
    for attempt in range(3):
        try:
            response = await client.aio.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=f"Сообщение:\n{text}",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
            )

            return float(response.text.strip()) > 0.75

        except Exception as e:
            print(f"Ошибка запроса к Gemini ({attempt + 1}/3): {e}")

            if attempt < 2:
                await asyncio.sleep(5)

    # Если все 3 попытки завершились ошибкой
    return False



