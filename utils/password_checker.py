import string



with open("utils/data/pop_passwords.txt", "r") as file:
    weak_passwords = file.readlines()

def checking(password: str) -> dict:
    """
    Критерии:
    - Длина не менее 8 символов
    - Наличие цифр, букв в верхнем и нижнем регистре, специальных символов
    - Отсутствие распространенных слабых паролей
    """
    result = {
        "code": 0,
        "text": ""
    }

    if len(password) < 8:
        result["text"] = "Слишком короткий пароль. Используйте минимум 8 символов:"
        return result

    if password.lower() in weak_passwords:
        result["text"] = "Пароль слишком распространен. Выберите более сложный пароль:"
        return result

    has_upper = any(c.isupper() for c in password)  # есть заглавные буквы
    has_lower = any(c.islower() for c in password)  # есть строчные буквы
    has_digit = any(c.isdigit() for c in password)  # есть цифры
    has_special = any(c in string.punctuation for c in password)  # есть спецсимволы

    score = "ulds"
    if has_upper:
        score = score.replace("u", "")
    if has_lower:
        score = score.replace("l", "")
    if has_digit:
        score = score.replace("d", "")
    if has_special:
        score = score.replace("s", "")

    recommendations = {"u":"заглавные буквы",
                       "l":"маленькие буквы",
                       "d":"цифры",
                       "s":"специальные символы"
                       }
    result_text = {
        0: "4/4 Отличный пароль!",
        1: f"3/4 Хороший пароль\nСовет: Добавьте {recommendations[score[0]]}",
        2: f"2/4 Слабый пароль\nСовет: Добавьте {recommendations[score[0]]} и {recommendations[score[1]]}",
        3: "1/4 Очень слабый пароль. Используйте разные регистры, цифры и специальные символы."
    }

    result["text"] = result_text[len(score)]
    result["code"] = 1
    return result
