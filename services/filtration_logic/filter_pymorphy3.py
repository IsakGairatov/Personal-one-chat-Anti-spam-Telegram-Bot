import re
import pymorphy3

from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent

morph = pymorphy3.MorphAnalyzer()


with open(BASE_DIR / "spam_words.json", "r", encoding="utf-8") as file:
    data = json.load(file)

SPAM_WORDS = data["words"]


async def find_spam_word(text: str) -> tuple[bool, str | None]:
    for word in re.findall(r"[а-яё]+", text.lower()):
        lemma = morph.parse(word)[0].normal_form

        if lemma in SPAM_WORDS:
            return True, lemma

    return False, None



