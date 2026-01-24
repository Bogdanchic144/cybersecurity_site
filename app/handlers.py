import asyncio
import app.keyboards as kb


from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode

from utils.password_generator import generate_passw
from utils.password_checker import checking
from utils.analysis_vt import get_file_info
from parce_meme import get_memes
from set_ai import set_prompt


class UserState(StatesGroup):
    waiting_for_answer = State()
    hints_response = State()
    current_index = State()
    user_password = State()
    password_len = State()
    prompt_ai = State()
    model_ai = State()
    wait_file = State()

router = Router()

@router.message(CommandStart())
async def cmd_start(message:Message, state:FSMContext):
    await state.clear()
    await message.answer((f"Привет! {(message.from_user.first_name + f" {message.from_user.last_name or ''}" )}"
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

@router.message(Command("virus_total"))
async def virus_total(message: Message, state: FSMContext):
    await state.clear()
    msg = await message.answer("Отправьте мне файл, чтобы я его проверил!")
    await state.set_state(UserState.wait_file)
    await state.update_data(wait_file=[msg.message_id, message.chat.id])

@router.message(UserState.wait_file)
async def analys_file(message: Message, state: FSMContext, bot: Bot):
    if doc := message.document:
        name: str = doc.file_name
        if doc.file_size < 20*1024*1024: # 20Mb
            await bot.download(doc.file_id, destination=f"app/total_files/{name}")
            await message.answer("Файл загружен! Анализирую файл...")

            result = await get_file_info(name)
            part_one = result.split("#S0S#")[0]
            part_two = result.split("#S0S#")[1]
            part_three = result.split("#S0S#")[2]
            await message.answer(part_one, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=kb.more_info)
            await message.answer(part_two, parse_mode=ParseMode.MARKDOWN_V2)
            await message.answer(part_three, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await message.answer(f"Файл слишком большой (Лимит 20Мб)")
            await message.answer('Вы можете его проверить на сайте '
                                 '[VirusTotal](https://www.virustotal.com/gui/home/upload)',
                                parse_mode=ParseMode.MARKDOWN_V2)

    else:
        data = await state.get_data()
        mess = data["wait_file"]
        await bot.send_message(mess[1], ".", reply_to_message_id=mess[0])

@router.callback_query(F.data == "vt_info")
async def vt_info(callback: CallbackQuery):
    info = """Вредоносный — Антивирус уверенно определил файл как вредоносный (вирус, троян и т.д.).\n
Подозрительный — Антивирус нашел подозрительные характеристики, но не уверен на 100%. 
Антивирус мог среагировать на подозрительные признаки, которые часто бывают у вирусов, или на код, 
который специально скрыт или защищён.\n
Не обнаружено — Антивирус не нашел ничего подозрительного в файле. 
Не означает "безопасный" — просто ничего не нашел.\n
Безопасный — Антивирус специально пометил файл как безопасный. 
Обычно для известных легитимных файлов (системные файлы Windows, ПО с хорошей репутацией)."""
    await callback.message.answer(info)

@router.message(Command("virus_practice"))
async def set_question(message: Message, state: FSMContext):
    await state.clear()
    with open("app/prompts/virus_prompt.txt", "r", encoding='utf-8') as file:
        prompt = file.read()
    await state.update_data(prompt_ai=prompt)
    await message.answer("Выберете модель", reply_markup=kb.model_ai_choose)

@router.message(Command("safety_practice"))
async def set_ask_safety(message: Message, state: FSMContext):
    await state.clear()
    with open("app/prompts/ask_safety_prompt.txt", "r", encoding='utf-8') as file:
        prompt = file.read()
    await state.update_data(prompt_ai=prompt)
    await message.answer("Выберете модель", reply_markup=kb.model_ai_choose)

@router.message(Command("tasks_practice"))
async def set_task(message:Message, state: FSMContext):
    await state.clear()
    with open("app/prompts/task_secure_prompt.txt", "r", encoding='utf-8') as file:
        prompt = file.read()
    await state.update_data(prompt_ai=prompt)
    await message.answer("Выберете модель", reply_markup=kb.model_ai_choose)

@router.callback_query(F.data.in_(["flash", "pro"]))
async def set_flash(callback: CallbackQuery, state: FSMContext):
    await state.update_data(model_ai=callback.data)
    await callback.message.answer("Выберете сложность", reply_markup=kb.levels)

@router.callback_query(F.data.in_(["hard", "medium", "easy"]))
async def set_request(callback: CallbackQuery, state: FSMContext):
    challenge = {
        "hard": "сложное",
        "medium": "среднее",
        "easy": "легкое"
    }

    data = await state.get_data()
    challenge_choose = challenge[callback.data]
    model = data["model_ai"]
    await callback.message.answer(f"Генерирую {challenge_choose} задание... (Режим: {model})")
    try:
        text_generation = await set_prompt(f"{data["prompt_ai"]}\nСоставь {challenge_choose} задание", model)
        # запрос ии
        if "Ошибка: " in text_generation:
            if "Error code: 429" in text_generation:
                await callback.message.answer("Токенов больше нет")
            else:
                await callback.message.answer(f"{text_generation}")

        if "polzovatel" in text_generation:
            text_generation = text_generation.replace("polzovatel",
                                                      (callback.message.from_user.last_name or "(Ваше имя)"))

        part_text = text_generation.split("___")
        task = part_text[0]
        question = part_text[1]

        await state.update_data(hints_response=part_text)
        await state.set_state(UserState.waiting_for_answer)
        await callback.message.answer(task)
        await callback.message.answer(question, reply_markup=kb.user_answer)

    except Exception as e:
        await callback.message.answer(f"Произошла ошибка, перезапустите бота (/start) и попробуйте снова\n\nError:{e}")

@router.message(UserState.waiting_for_answer, F.text.in_(["Да", "Нет"]))
async def check_answer(message:Message, state: FSMContext):
    data = await state.get_data()
    response = data.get('hints_response')
    true_answer = response[2]
    explanation = response[3]

    if message.text in true_answer:
        await message.answer(f"Правильно✅\n{explanation}", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(f"Неправильно❌\n{explanation}", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@router.message(F.text == "Подсказка")
async def helping_test(message:Message, state:FSMContext):
    data = await state.get_data()
    hints = data.get('hints_response')[4]
    current_index = data.get('current_index', 0)

    if not hints:
        return

    sps_helps = []
    while "#1" in hints:
        start = hints.find("#1") + 2
        end = hints.find("#2")

        if start != -1 and end != -1:
            result = hints[start:end].strip()
            sps_helps.append(result)
            hints = hints[end + 2:]
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

@router.message(F.text)
async def any_message(message: Message):
    await message.answer("Эээ...")
    await asyncio.sleep(1)
    await message.answer("эт че?")