import json
import re

import pymorphy3


morph = pymorphy3.MorphAnalyzer()


with open("spam_words.json", "r", encoding="utf-8") as file:
    data = json.load(file)

SPAM_WORDS = data["words"]


def find_spam_word(text: str) -> tuple[bool, str | None]:
    for word in re.findall(r"[а-яё]+", text.lower()):
        lemma = morph.parse(word)[0].normal_form

        if lemma in SPAM_WORDS:
            return True, lemma

    return False, None



