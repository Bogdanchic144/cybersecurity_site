import string
from random import randint



with open("utils/data/words.txt", "r") as f:
    sps_word = sorted([word for word in f.read().splitlines()], key=len)

def generation(length: int = 12) -> dict:
    result = {
        "code": 0,
        "text": ""
              }

    if  length < 8:
        result["text"] = "Минимальная длина пароля - 8 символов"
        return result

    if length > 100:
        result["text"] = "Длина пароля не должна превышать 100 символов"
        return result

    random_len = [word for word in sps_word if len(word) == (length - randint(3, (length - 2)))] # 12 - randint(3, 10)
  # ^^^^^^^^^^ слова указанной длины (length - random)
    random_registr = []
    for word in random_len: # слова с разными регистром
        rint = randint(1, len(word)-1)
        random_registr.append(word[:rint].upper() + word[rint:])

    spec_simv = string.punctuation # спец символы
    numbers = "0123456789"
    randword = random_registr[randint(0, len(random_registr)-1)]
    password = randword + numbers[randint(0, 9)] + spec_simv[randint(0, len(spec_simv))]
    # гарантирует что есть 1 цифра и 1 спец символ

    for i in range(length-len(randword)-2): # оставшиеся незаполненые символы
        n_or_s = [spec_simv, numbers][randint(0,1)]
        n_or_s = n_or_s[randint(0, len(n_or_s)-1)]
        password += n_or_s

    result["code"] = 1
    result["text"] = password
    return result
