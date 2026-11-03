import asyncio
from Gemini_googling2 import ask_ai

async def main():
    print(await ask_ai(
        "Какая последняя версия ACE-Step? Найди информацию в интернете."
    ))

asyncio.run(main())