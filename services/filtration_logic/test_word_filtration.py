from services.filtration_logic.filter_pymorphy3 import find_spam_word


def test_has_spam_words():
    test_cases = [
        ("Нужна замена на шабашку 5500 на руки Компенсируем проезды Актуально", True),
        ("Сегодня хорошая погода, пойдём гулять?", False),
        ("Требуется помощь, 6000 за пару часов. Пиши", True),
        ("Я вчера смотрел новый фильм", False),
        ("Занятость на свежем воздухе 6.000 на руки Обеды и отдых включительно Писать - @ksoynx", True),
        ("Внимание: работа через телефон, до 3 часов в день, без сложностей. Подходит всем. Пишите в ЛС.", True),
        ("Мне нужно купить продукты на ужин", False),
        ("Litenergy ищет приемщиков продукции энергетиков 5 800 на руки Пиши - @tvoyavakansia", True),
        ("Завтра у нас будет контрольная работа", False),
        ("Есть вакансия на сегодня и завтра, наличие авто приветствуется", True),
        ("Моя кошка спит на диване", False),
        ("Ищем помощников нужно убрать дачу, оплатим и накормим, деньги нужны пишите в лс", True),
    ]

    for text, expected in test_cases:
        result = find_spam_word(text)[0]

        print(
            f"{'PASS' if result == expected else 'FAIL'} | "
            f"{result} | {text}"
        )

msg1 = '''россиянин сам себя зацензурил, лишь бы не видеть правду о себе. ммм, ничего нового. не знала только, что он депутат.'''


import json
from collections import Counter


def analyze_messages(
    input_file: str,
    output_file: str,
):
    with open(input_file, "r", encoding="utf-8") as file:
        messages = json.load(file)

    spam_messages = []
    spam_words_stats = Counter()

    for message in messages:
        text = message.get("text", "")

        if not text:
            continue

        is_spam, spam_word = find_spam_word(text)

        if not is_spam:
            continue

        spam_messages.append({
            **message,
            "spam_word": spam_word,
        })

        spam_words_stats[spam_word] += 1

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            spam_messages,
            file,
            ensure_ascii=False,
            indent=4,
        )

    print(f"Всего сообщений: {len(messages)}")
    print(f"Найдено спам-сообщений: {len(spam_messages)}")

    print("\nСтатистика по словам:")

    for word, count in spam_words_stats.most_common():
        print(f"{word}: {count}")

