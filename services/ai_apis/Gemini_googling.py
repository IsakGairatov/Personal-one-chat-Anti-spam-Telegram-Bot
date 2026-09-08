from dotenv import load_dotenv
from google import genai
from google.genai import types
from config import GEMINI_GOOGLING_API_KEY


load_dotenv()

client = genai.Client(
    api_key=GEMINI_GOOGLING_API_KEY
)


SYSTEM_PROMPT = """Ты — AI-ассистент в Telegram-чате.

Отвечай кратко, понятно и прямо на вопрос пользователя.
Не добавляй лишних вступлений и пояснений.
Если вопрос простой — ответь в 1–3 предложениях.
Отвечай на языке вопроса.
"""


async def ask_ai(text: str) -> str:
    response = await client.aio.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"Сообщение:\n{text}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        ),
    )

    return response.text.strip()



