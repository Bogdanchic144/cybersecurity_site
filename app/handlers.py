import app.keyboards as kb

from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from parce_meme import get_memes
from set_ai import set_prompt
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from generate_password import generate_passw
from check_passw import checking


class UserState(StatesGroup):
    waiting_for_answer = State()
    current_text_generation = State()
    current_index = State()
    user_password = State()
    password_len = State()
    prompt_ai = State()

router = Router()

@router.message(CommandStart())
async def cmd_start(message:Message, state:FSMContext):
    await state.clear()
    await message.answer(("Привет! 👋"
"\nЯ — твой персональный тренажёр по цифровой безопасности."
"\nЗдесь ты можешь потренироваться распознавать мошенников, прокачать навыки защиты своих данных, "
"проверим надёжность твоих паролей и научим безопасно вести себя в интернете."
"\n\nЯ буду давать тебе задания: от лёгких до продвинутых, из реальных ситуаций и бытовых сценариев."
"\nГотов проверить себя и стать чуть менее уязвимым в сети? 🚀"), reply_markup=ReplyKeyboardRemove())


@router.message(Command("get_memes"))
async def get_meme(message:Message):
    await message.answer_photo(photo=get_memes())

@router.message(Command("password"))
async def password(message:Message):
    await message.answer("Здесь ты можешь проверить или сгенерировать пароль", reply_markup=kb.password_choose)

@router.message(F.text == "Сгенерировать")
async def gen_password(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Длина пароля:")
    await state.set_state(UserState.password_len)

@router.message(UserState.password_len)
async def gen_password2(message: Message, state: FSMContext):
    try:
        await state.update_data(password_len=message.text)
        data = await state.get_data()
        gen_pass = generate_passw(int(data["password_len"]))
        if gen_pass == "Длина пароля должна быть не менее 8 и не более 100 символов":
            await message.answer(f"{gen_pass}")
        else:
            await message.answer(f"{gen_pass}")
            await state.clear()
    except:
        await message.answer("Введите число!")


@router.message(F.text == "Проверить")
async def check_password(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите пароль, который хотите проверить:")
    await state.set_state(UserState.user_password)

@router.message(UserState.user_password)
async def check_password2(message: Message, state: FSMContext):
    await state.update_data(user_password=message.text)
    data = await state.get_data()
    result = await checking(data["user_password"])
    await message.answer(result)
    if (result != "Пароль слишком распространен. Выберите более сложный пароль."
            and result != "Слишком короткий пароль. Используйте минимум 8 символов."):
        await state.clear()

@router.message(Command("safety_check"))
async def set_ask_safety(message: Message, state: FSMContext):
    await state.clear()
    with open("app/prompts/ask_safety_prompt.txt", "r", encoding='utf-8') as file:
        prompt = file.read()
    await state.update_data(prompt_ai=prompt)
    await message.answer("Выберете сложность", reply_markup=kb.levels)

@router.message(Command("tasks"))
async def set_task(message:Message, state: FSMContext):
    await state.clear()
    with open("app/prompts/task_secure_prompt.txt", "r", encoding='utf-8') as file:
        prompt = file.read()
    await state.update_data(prompt_ai=prompt)
    await message.answer("Выберете сложность", reply_markup=kb.levels)

@router.callback_query(F.data.in_(["hard", "medium", "easy"]))
async def set_request(callback: CallbackQuery, state: FSMContext):
    difficulty_map = {
        "hard": "сложное",
        "medium": "среднее",
        "easy": "легкое"
    }

    data = await state.get_data()
    difficulty_choose = difficulty_map[callback.data]
    await callback.message.answer(f"Генерирую {difficulty_choose} задание...")
    try:
        text_generation = await set_prompt(f"{data["prompt_ai"]}\nСоставь {difficulty_choose} задание") # запрос ии
        await state.update_data(current_text_generation=text_generation)
        await state.set_state(UserState.waiting_for_answer)
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка, перезапустите бота (/start) и попробуйте снова\n\nError:{e}")

    def formating(begin, finish):
        noformat_text = text_generation
        if "#us#" in noformat_text:
            try:
                noformat_text = noformat_text.replace("#us#", f"{callback.message.from_user.last_name}")
            except Exception as e:
                noformat_text = noformat_text.replace("#us#", "(Ваше имя)")
                print(f"Ошибка:{e}")

        start = noformat_text.find(begin) + len(begin)
        end = noformat_text.find(finish)

        if start != -1 and end != -1:
            result = noformat_text[start:end].strip()
            return result
        else:
            print("Метки не найдены")
            return "Ошибка форматирования"

    await callback.message.answer(text=formating("#ЗН#", "#ЗК#"))
    await callback.message.answer(text=formating("#ВН#", "#ВК#"), reply_markup=kb.user_answer)

@router.message(UserState.waiting_for_answer, F.text.in_(["Да", "Нет"]))
async def check_answer(message:Message, state: FSMContext):
    data = await state.get_data()
    text = data.get('current_text_generation')
    true_answer = text[text.find("#О#") + 3:]
    start_ta = true_answer.find("#1") + 2
    end_ta = true_answer.find("#2")
    if message.text in true_answer[start_ta:end_ta]:
        await message.answer(f"Правильно✅\n{true_answer[end_ta+2:]}", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(f"Неправильно❌\n{true_answer[end_ta+2:]}", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(F.text == "Подсказка")
async def helping_test(message:Message, state:FSMContext):
    data = await state.get_data()
    text = data.get('current_text_generation')
    current_index = data.get('current_index', 0)

    if not text:
        return

    sps_helps = []
    while "#ПН#" in text:
        start = text.find("#ПН#") + 4
        end = text.find("#ПК#")

        if start != -1 and end != -1:
            result = text[start:end].strip()
            sps_helps.append(result)
            text = text[end + 4:]
        else:
            break

    if not sps_helps:
        await message.answer("В тексте нет подсказок")
        return

    if current_index < len(sps_helps):
        await message.answer(f"Подсказка {current_index + 1}: {sps_helps[current_index]}")
        current_index += 1
        await state.update_data(current_index=current_index)
    else:
        await message.answer("Подсказки закончились!")
