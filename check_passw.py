import string

async def checking(password: str) -> str | tuple[str, bool]:
    """
    Критерии:
    - Длина не менее 8 символов
    - Наличие цифр, букв в верхнем и нижнем регистре, специальных символов
    - Отсутствие распространенных слабых паролей
    """

    if len(password) < 8:
        return "Слишком короткий пароль. Используйте минимум 8 символов."

    weak_passwords = ["123456", "123456789", "12345678", "password", "qwerty123", "qwerty1", "111111", "12345", "Secret", "123123", "1234567890", "1234567", "000000", "qwerty", "abc123", "password1", "iloveyou", "11111111", "dragon", "monkey"]
    if password.lower() in weak_passwords:
        return "Пароль слишком распространен. Выберите более сложный пароль."

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

    if len(score) == 0:
        return "4/4 Отличный пароль!"
    elif len(score) == 1:
        return f"3/4 Хороший пароль\nСовет: Добавьте {recommendations[score[0]]}"
    elif len(score) == 2:
        return f"2/4 Слабый пароль\nСовет: Добавьте {recommendations[score[0]]} и {recommendations[score[1]]}"
    else:
        return "1/4 Очень слабый пароль. Используйте разные регистры, цифры и специальные символы."

