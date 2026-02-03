from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

levels = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Сложно", callback_data="hard")],
    [InlineKeyboardButton(text="Норм", callback_data="medium")],
    [InlineKeyboardButton(text="Легко", callback_data="easy")]
])

model_ai_choose = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Flash", callback_data="flash")],
    [InlineKeyboardButton(text="Pro", callback_data="pro")]
])

user_answer = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
    [KeyboardButton(text="Подсказка")]
], resize_keyboard=True)

password_choose = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Сгенерировать"), KeyboardButton(text="Проверить")]
], resize_keyboard=True)

more_info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Чего?", callback_data="vt_info")],
])

continue_or_no = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Продолжить")]
], resize_keyboard=True, one_time_keyboard=True)

all_functions = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Пароли")],
    [KeyboardButton(text="Безопасность в сети")],
    [KeyboardButton(text="Мошенники")],
    [KeyboardButton(text="Вирусы")],
    [KeyboardButton(text="Статистика")],
    [KeyboardButton(text="Проверка файлов на вирусы")]
], resize_keyboard=True, one_time_keyboard=True)