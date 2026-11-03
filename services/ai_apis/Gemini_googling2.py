import asyncio
import requests

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

from config import GEMINI_GOOGLING_API_KEY, LANGSEARCH_API_KEY


# --------------------------------------------------
# Configuration
# --------------------------------------------------

MODEL = "gemini-3.5-flash-lite"
LANGSEARCH_URL = "https://api.langsearch.com/v1/web-search"

MAX_SEARCH_CALLS = 3
MAX_ROUNDS = 5


# --------------------------------------------------
# Gemini
# --------------------------------------------------

client = genai.Client(
    api_key=GEMINI_GOOGLING_API_KEY
)


# --------------------------------------------------
# System prompt
# --------------------------------------------------

SYSTEM_PROMPT = """Ты — AI-ассистент в Telegram-чате.

Отвечай кратко, понятно и прямо на вопрос пользователя.
Не добавляй лишних вступлений и пояснений.
Если вопрос простой — ответь в 1–3 предложениях.
Отвечай на языке вопроса.

У тебя есть инструмент поиска в интернете.

Правила использования поиска:
- Если что-то не знаешь, или не уверен, 
сначала прогугли в поиске, а не уточняй у пользователя.
- Используй поиск, когда нужны актуальные сведения,
  новости, свежие данные или информация, которой
  может не быть в твоих знаниях.
- Не используй поиск для обычных разговоров,
  простых объяснений и общих знаний.
- Если пользователь просит найти или проверить
  информацию в интернете — обязательно используй поиск.
- Не выдумывай результаты поиска и источники.
- При использовании найденной информации указывай
  ссылки на источники в формате Markdown.
- Если источники противоречат друг другу,
  сообщи об этом.
  
Форматирование ответа:
- Используй Telegram Markdown (legacy).
- Для жирного текста используй *текст*, не **текст**.
- Для курсива используй _текст_.
- Ссылки оформляй как [название источника](URL).
- Не выводи названия источников в квадратных скобках без URL.
- Не выдумывай ссылки и источники.
"""


# --------------------------------------------------
# LangSearch
# --------------------------------------------------

def _search_web(query: str) -> dict:
    """Синхронный запрос к LangSearch."""

    if not LANGSEARCH_API_KEY:
        return {"error": "LANGSEARCH_API_KEY не настроен."}

    response = requests.post(
        LANGSEARCH_URL,
        headers={
            "Authorization": f"Bearer {LANGSEARCH_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "count": 5,
            "contents": {
                "text": {
                    "max_characters": 2500
                }
            },
        },
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    if str(payload.get("code")) != "200":
        return {
            "error": payload.get("message", "Ошибка LangSearch"),
            "code": payload.get("code"),
        }

    pages = (
        payload.get("data", {})
        .get("webPages", {})
        .get("value", [])
    )

    results = []

    for page in pages:
        results.append({
            "title": page.get("name", ""),
            "url": page.get("url", ""),
            "date": page.get("datePublished"),
            "content": (
                page.get("text")
                or page.get("snippet")
                or ""
            ),
        })

    return {
        "query": query,
        "results": results,
    }


async def search_web(query: str) -> dict:
    """Асинхронный поиск."""

    try:
        return await asyncio.to_thread(
            _search_web,
            query,
        )

    except requests.RequestException as e:
        return {"error": f"Ошибка LangSearch: {e}"}

    except (ValueError, KeyError) as e:
        return {"error": f"Ошибка обработки результатов: {e}"}


# --------------------------------------------------
# Function declaration
# --------------------------------------------------

search_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_web",
            description=(
                "Ищет актуальную информацию в интернете "
                "через LangSearch. Возвращает заголовки, "
                "ссылки и содержимое найденных страниц."
            ),
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Поисковый запрос.",
                    }
                },
                "required": ["query"],
            },
        )
    ]
)


# --------------------------------------------------
# Ask AI
# --------------------------------------------------

async def ask_ai(text: str) -> str:

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"Сообщение:\n{text}"
                )
            ],
        )
    ]

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[search_tool],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode="AUTO"
            )
        ),
        temperature=0.7,
    )

    search_calls = 0

    for _ in range(MAX_ROUNDS):

        response = await client.aio.models.generate_content(
            model=MODEL,
            contents=contents,
            config=config,
        )

        if not response.candidates:
            return "Gemini не вернул ответ."

        candidate = response.candidates[0]
        model_content = candidate.content

        if not model_content or not model_content.parts:
            return (
                response.text
                or "Не удалось сформировать ответ."
            ).strip()

        calls = [
            part.function_call
            for part in model_content.parts
            if part.function_call is not None
        ]

        # Gemini сформировал обычный ответ.
        if not calls:
            return (
                response.text
                or "Не удалось сформировать ответ."
            ).strip()

        # Сохраняем вызовы функций в истории.
        contents.append(model_content)

        tool_response_parts = []

        for call in calls:

            if call.name != "search_web":
                continue

            if search_calls >= MAX_SEARCH_CALLS:
                result = {
                    "error": "Достигнут лимит поисковых вызовов."
                }

            else:
                query = (call.args or {}).get("query", "").strip()

                if not query:
                    result = {"error": "Пустой поисковый запрос."}

                else:
                    search_calls += 1
                    result = await search_web(query)

            tool_response_parts.append(
                types.Part.from_function_response(
                    name=call.name,
                    response=result,
                )
            )

        if not tool_response_parts:
            return "Не удалось выполнить поисковый запрос."

        # Передаём результаты функций обратно Gemini.
        # Для Gemini API используется role="user".
        contents.append(
            types.Content(
                role="user",
                parts=tool_response_parts,
            )
        )

    return "Не удалось завершить обработку запроса: превышен лимит обращений к модели."