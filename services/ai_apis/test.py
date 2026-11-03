import asyncio
from Gemini_googling2 import ask_ai

async def main():
    print(await ask_ai(
        "Что произошло 3 ноября 2026 года в киеве?"
    ))

asyncio.run(main())