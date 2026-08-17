import json
import pymorphy3
import re

morph = pymorphy3.MorphAnalyzer()

def lemmatize(text: str) -> str:
    words = re.findall(r"[а-яё]+", text.lower())

    return ' '.join([
        morph.parse(word)[0].normal_form
        for word in words
    ])


with open("words.txt", "r", encoding="utf-8") as file:
    text = file.read()

words = {
    lemmatize(word.strip())
    for word in text.split(";")
    if word.strip()
}

with open("spam_words0.json", "w", encoding="utf-8") as file:
    json.dump(list(words), file, ensure_ascii=False, indent=4)