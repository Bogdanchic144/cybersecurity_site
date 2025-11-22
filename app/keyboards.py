from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

levels = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Сложно", callback_data="hard")],
    [InlineKeyboardButton(text="Норм", callback_data="medium")],
    [InlineKeyboardButton(text="Легко", callback_data="easy")]
])

user_answer = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
    [KeyboardButton(text="Подсказка")]
], resize_keyboard=True)

password_choose = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Сгенерировать"), KeyboardButton(text="Проверить")]
], resize_keyboard=True)
