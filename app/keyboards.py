from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

levels = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Сложно", callback_data="hard")],
    [InlineKeyboardButton(text="Норм", callback_data="medium")],
    [InlineKeyboardButton(text="Легко", callback_data="easy")]
])

model_ai_choose = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="2.5", callback_data="gemini-2.5-flash")],
    [InlineKeyboardButton(text="3", callback_data="gemini-3-flash-preview")]
])

user_answer = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
    [KeyboardButton(text="Подсказка")]
], resize_keyboard=True)

password_choose = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Сгенерировать"), KeyboardButton(text="Проверить")]
], resize_keyboard=True, input_field_placeholder="Выберите функцию")

more_info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Чего?", callback_data="vt_info")],
])

continue_or_no = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Продолжить")]
], resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Нажмите \"Продолжить\"")

all_functions = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Пароли")],
    [KeyboardButton(text="Безопасность в сети")],
    [KeyboardButton(text="Мошенники")],
    [KeyboardButton(text="Вирусы")],
    [KeyboardButton(text="Статистика")],
    [KeyboardButton(text="Проверка файлов на вирусы")]
], resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Выберите пункт меню")

async def button_answers(list_buttons: list) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    for button in list_buttons:
        keyboard.add(KeyboardButton(text=button))
    return keyboard.adjust(1).as_markup(resize_keyboard=True)