import asyncio

import aiofiles

import app.keyboards as kb

from aiogram.filters.command import CommandObject
from aiogram.filters import CommandStart, Command, Filter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode

from utils.password_generator import generation
from utils.password_checker import checking
from utils.analysis_vt import get_file_info
from set_ai import send_prompt
from forDB.db_service import DB



class UserState(StatesGroup):
    waiting_for_answer = State()
    correct_answer_virus = State()
    hints_response = State()
    current_index = State()
    user_password = State()
    password_len = State()
    model_ai = State()
    challenge = State()
    wait_file = State()
    ai_chat = State()
    path_task = State()
    explanation = State()

router = Router()

#                                                                                                             START_FUNC

@router.message(CommandStart())
async def cmd_start(message:Message, state:FSMContext, command: CommandObject):
    await state.clear()
    await DB.insert_user(message.from_user.id)
    await asyncio.sleep(1)

    params_to_func = {
        "virus": {"func": set_virus,
                             "text": "Привет! Я вижу, вы перешли из раздела «Вирусы». Всё готово к практике!"},
        "password": {"func": password,
                               "text": "Привет! Я вижу, вы перешли из раздела «Пароли». Всё готово к практике!"},
        "safety": {"func": set_safety,
                            "text": "Привет! Я вижу, вы перешли из раздела «Безопасность в сети». Всё готово к практике!"},
        "scum": {"func": set_scum,
                           "text": "Привет! Я вижу, вы перешли из раздела «Мошенники». Всё готово к практике!"}
    }

    if command.args:
        param = command.args
        if param in params_to_func:
            func = params_to_func[param]["func"]
            text = params_to_func[param]["text"]
            await message.answer(text)
            await func(message, state)
        else:
            await message.answer((f"Привет! {(message.from_user.last_name or message.from_user.first_name)}"
                                  "\nЯ — твой персональный тренажёр по цифровой безопасности."
                                  "\nЗдесь ты можешь потренироваться распознавать мошенников, прокачать навыки защиты своих данных, "
                                  "проверим надёжность твоих паролей и научим безопасно вести себя в интернете."
                                  "\n\nЯ буду давать тебе задания: от лёгких до продвинутых, из реальных ситуаций и бытовых сценариев."
                                  "\nГотов проверить себя и стать чуть менее уязвимым в сети? 🚀"),
                                 reply_markup=kb.all_functions)
    else:
        await message.answer((f"Привет! {(message.from_user.last_name or message.from_user.first_name)}"
                  "\nЯ — твой персональный тренажёр по цифровой безопасности."
                  "\nЗдесь ты можешь потренироваться распознавать мошенников, прокачать навыки защиты своих данных, "
                  "проверим надёжность твоих паролей и научим безопасно вести себя в интернете."
                  "\n\nЯ буду давать тебе задания: от лёгких до продвинутых, из реальных ситуаций и бытовых сценариев."
                  "\nГотов проверить себя и стать чуть менее уязвимым в сети? 🚀"),
                 reply_markup=kb.all_functions)

# @router.message(Command("write_ai"))
# async def get_meme(message:Message, state: FSMContext):
    # hello_ai = await set_prompt("Напиши приветствие и расскажи что ты умеешь", "flash")
    # await message.answer(hello_ai)
    # await state.set_state(UserState.ai_chat)

#                                                                                                          PASSWORD_FUNC

@router.message(F.text == "Пароли")
@router.message(Command("password"))
async def password(message:Message, state: FSMContext):
    await state.clear()
    await message.answer("Здесь вы научитесь создавать надежные пароли и проверите их устойчивость ко взлому",
                         reply_markup=kb.password_choose)

@router.message(F.text == "Сгенерировать")
async def get_length_password(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Длина пароля:")
    await state.set_state(UserState.password_len)

@router.message(UserState.password_len)
async def generation_password(message: Message, state: FSMContext):
    try:
        await state.update_data(password_len=message.text)
        data = await state.get_data()
        length_pass = int(data["password_len"])
        result = generation(length_pass)

        if result["code"] == 1:
            await message.answer(result["text"], reply_markup=kb.password_choose)
            await state.clear()
        else:
            await message.answer((result["text"]))

    except ValueError:
        await message.answer("Введите целое число!")
    except Exception as e:
        await message.answer(f"Неожиданныя ошибка!\n{e}")

@router.message(F.text == "Проверить")
async def get_password(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите пароль, который хотите проверить:")
    await state.set_state(UserState.user_password)

@router.message(UserState.user_password)
async def check_password(message: Message, state: FSMContext):
    await state.update_data(user_password=message.text)
    data = await state.get_data()
    result = checking(data["user_password"])
    await message.answer(result["text"])
    if result["code"] == 1:
        await state.clear()

#                                                                                                       VIRUS_TOTAL_FUNC

@router.message(F.text == "Проверка файлов на вирусы")
@router.message(Command("virus_total"))
async def virus_total(message: Message, state: FSMContext):
    await state.clear()
    msg = await message.answer("Отправьте мне файл, чтобы VirusTotal его проверил!",
                               reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserState.wait_file)
    await state.update_data(wait_file=[msg.message_id, message.chat.id])

@router.message(UserState.wait_file)
async def analys_file(message: Message, state: FSMContext, bot: Bot):
    if doc := message.document:
        await state.clear()
        name: str = doc.file_name
        if doc.file_size < 20*1024*1024: # 20Mb
            await bot.download(doc.file_id, destination=f"app/{name}")
            await message.answer("Файл загружен! Анализирую файл...")

            result = await get_file_info(name)
            result = result.split("#S0S#")
            part_one = result[0]
            part_two = result[1]
            part_three = result[2]
            await message.answer(part_one, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=kb.more_info)
            await message.answer(part_two, parse_mode=ParseMode.MARKDOWN_V2)
            await message.answer(part_three, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=kb.all_functions)
        else:
            await message.answer(f"Файл слишком большой (Лимит 20Мб)")
            await message.answer('Вы можете его проверить на сайте '
                                 '[VirusTotal](https://www.virustotal.com/gui/home/upload)',
                                parse_mode=ParseMode.MARKDOWN_V2, reply_markup=kb.all_functions)

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

#                                                                                                          PRACTICE_FUNC

# @router.message(F.text == "Меню")
# async def restart(message: Message, state: FSMContext):
#     state = await state.get_data()

async def construct_request(message: Message, state: FSMContext, path):
    await state.clear()
    await state.update_data(path_task=path)
    await message.answer("Выберите модель gigachat"
                         "\n(Для лучшего опыта выберите модель Pro, "
                         "остальные модели нестабильны и могут вызывать ошибки",
                         reply_markup=kb.model_ai_choose)

@router.message(F.text == "Вирусы")
@router.message(Command("viruses_practice"))
async def set_virus(message: Message, state: FSMContext):
    await message.answer("В этом разделе вы отработаете навыки распознания вредоносных файлов с вирусами.")
    await construct_request(message, state, "app/prompts/virus/")

@router.message(F.text == "Безопасность в сети")
@router.message(Command("safety_practice"))
async def set_safety(message: Message, state: FSMContext):
    await message.answer("В этом разделе вы проанализируете реальные кейсы киберугроз и "
                         "освоите практические навыки для защиты в интернете.")
    await construct_request(message, state, "app/prompts/safety/")

@router.message(F.text == "Мошенники")
@router.message(Command("scummers_practice"))
async def set_scum(message:Message, state: FSMContext):
    await message.answer("Здесь вы научитесь распознавать мошеннические схемы и "
                         "принимать правильные решения в опасных ситуациях.")
    await construct_request(message, state, "app/prompts/scum/")

#                                                                                                   choose-PRACTICE_FUNC

@router.callback_query(F.data.in_(["GigaChat-2", "GigaChat-2-Pro", "GigaChat-2-Max"]))
async def set_model(callback: CallbackQuery, state: FSMContext):
    await state.update_data(model_ai=callback.data)
    await callback.message.answer("Выберете сложность", reply_markup=kb.levels)

@router.callback_query(F.data.in_(["hard", "medium", "easy"]))
async def set_challenge(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    challenge_choose = callback.data
    model_ai = data["model_ai"]

    await state.update_data(challenge=challenge_choose)
    await callback.message.answer(
        f"Ваш запрос:\n⚙️ {challenge_choose} task\n🤖 {model_ai}\n\n"
        f"Нажмите 'Продолжить' для генерации задачи",
        reply_markup=kb.continue_or_no
    )

#                                                                                               generation-PRACTICE_FUNC

async def get_ai_text(message, state) -> dict | None:
    data = await state.get_data()

    if ("challenge" not in data) or ("model_ai" not in data):
        await message.answer(
            "Произошла ошибка. Начните заново /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return None

    challenge_choose = data["challenge"]
    model = data["model_ai"]
    path_task = data["path_task"]

    async with aiofiles.open(f"{path_task + challenge_choose + '.txt'}", "r", encoding='utf-8') as file:
        prompt = await file.read()

    max_retries = 5
    retry_delay = 2
    to_delete = await message.answer("Секунду...", reply_markup=ReplyKeyboardRemove())
    for attempt in range(max_retries):
        try:
            text_generation = await send_prompt(prompt, model) if \
                (path_task + challenge_choose != 'app/prompts/virus/hard') \
                else "1-----2-----3-----4-----5" #УДАЛИТЬ! после реализации
            print(text_generation)
            # запрос ии

            # async with aiofiles.open(f"files/test.txt", "r", encoding='utf-8') as file:
            #     text_generation = await file.read()

            if "Error:" in text_generation:
                if "Error:429" in text_generation:
                    await message.answer("Токены закончились, выберите другую модель")
                    return None
                elif "Error:5" in text_generation:
                    if attempt < max_retries - 1:
                        await to_delete.edit_text(f"Сервер не отвечает, пробуем ещё раз..."
                                                  f"\n(Попытка {attempt + 1}/{max_retries})")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        await to_delete.edit_text("Сервер не отвежает после нескольких попыток. Попробуйте позже.")
                        return None
                else:
                    await to_delete.edit_text(f"{text_generation}")
                    return None

            if "polzovatel" in text_generation:
                text_generation = text_generation.replace(
                    "polzovatel",
                    (message.from_user.last_name or message.from_user.first_name or "Бро")
                )

            result = {
                "text": text_generation,
                "challenge": challenge_choose,
                "practice": path_task.split("/")[-2]
            }

            await to_delete.delete()
            return result

        except Exception as e:
            await message.answer(f"Произошла ошибка, перезапустите бота (/start) и попробуйте снова\n\nError:{e}")
    return None


class TextInListFilter(Filter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        data = await state.get_data()
        answers = list(map(lambda string: string[:30], data["waiting_for_answer"])) if "waiting_for_answer" in data else []
        msg = message.text.strip()[:30]
        return msg in answers

@router.message(F.text == "Продолжить")
async def set_request(message: Message, state: FSMContext):

    async def scum_func(text: str, challenge: str):
        await message.answer("Это альфа версия задач по мошенникам, новая версия в разработке...")
        part_text = text.split("-----")
        task = part_text[0]
        question = part_text[1]

        await state.update_data(hints_response=part_text)
        await state.set_state(UserState.waiting_for_answer)
        await message.answer(task)
        await message.answer(question, reply_markup=kb.user_answer)

    async def virus_func(text: str, challenge: str):

        async def easy_func(etext: str):
            part_text = etext.split("-----")
            question = part_text[0]
            answer_option = []
            correct_answer = part_text[1]

            n = 1
            while f"#{n}#" in question:
                start = question.find(f"#{n}#") + 3
                end = question.find(f"#{n + 1}#")

                answer_option.append(f"{n}) " + question[start:end].strip())
                question = question.replace(question[start-3:end], f"\n{n}) {question[start:end]}")
                n += 1

            await message.answer(question, reply_markup=await kb.button_answers(answer_option))
            await state.update_data(waiting_for_answer=answer_option)
            await state.update_data(correct_answer_virus=correct_answer)
            await state.set_state(UserState.waiting_for_answer)

        async def medium_func(mtext: str):
            part_text = mtext.split("-----")
            question = part_text[0]
            raw_answer_option = part_text[1]
            correct_answer = part_text[2]
            explanation = part_text[3]

            answer_option = []
            n = 1
            while f"#{n}#" in raw_answer_option:
                begin = raw_answer_option.find(f"#{n}#") + 3
                end = raw_answer_option.find(f"#{n + 1}#")
                answer_option.append(f"{n}) " + raw_answer_option[begin:end].strip())
                raw_answer_option = raw_answer_option.replace(f"#{n}#", f"\n{n}) ")
                n += 1

            await message.answer(question)
            await message.answer(raw_answer_option, reply_markup=await kb.button_answers(answer_option))
            await state.update_data(waiting_for_answer=answer_option)
            await state.update_data(correct_answer_virus=correct_answer)
            await state.update_data(explanation=explanation)
            await state.set_state(UserState.waiting_for_answer)

        async def hard_func(htext: str):
            await message.answer("🛠️ 'Практика по вирусам - сложно' находится в разработке...")
            await asyncio.sleep(2)
            await message.answer("Но вы можете попробовать другую сложность в данной практике")

        challenge_dict = {
            "easy": easy_func,
            "medium": medium_func,
            "hard": hard_func
        }

        await challenge_dict[challenge](text)

    async def safety_func(text: str, challenge: str):
        await message.answer("Это альфа версия задач по безопасности в сети, новая версия в разработке...")
        part_text = text.split("-----")
        task = part_text[0]
        question = part_text[1]

        await state.update_data(hints_response=part_text)
        await state.set_state(UserState.waiting_for_answer)
        await message.answer(task)
        await message.answer(question, reply_markup=kb.user_answer)

    func_dict = {
        "scum": scum_func,
        "virus": virus_func,
        "safety": safety_func
    }

    data = await get_ai_text(message, state)
    ai_text = data["text"]
    practice = data["practice"]
    challenge = data["challenge"]
    await func_dict[practice](ai_text, challenge)

#                                                                                                   answer-FRACTICE_FUNC

@router.message(UserState.waiting_for_answer, TextInListFilter())
async def check_answer_u(message: Message, state: FSMContext):
    data = await state.get_data()

    explanation = data["explanation"] if ("explanation" in data) else ""

    correct_answer = data["correct_answer_virus"]
    begin = correct_answer.find("#")
    end = correct_answer.find("#", begin + 1)
    correct_answer = correct_answer[begin + 1:end]

    user_answer = message.text
    if user_answer[0] in correct_answer:
        await message.answer("✅ Верно!", reply_markup=kb.continue_or_no)
        await DB.update_data(message.from_user.id, add_correct_answer=1)
    else:
        await message.answer(f"❌ Неверно(\n Правильный ответ: {correct_answer}\n{explanation}", reply_markup=kb.continue_or_no)
        await DB.update_data(message.from_user.id, add_incorrect_answer=1)

#                                                                                                   yes/no-PRACTICE_FUNC

@router.message(UserState.waiting_for_answer, F.text.in_(["Да", "Нет"]))
async def check_answer(message:Message, state: FSMContext):
    data = await state.get_data()
    response = data.get('hints_response')
    true_answer = response[2].upper()
    explanation = response[3]

    if message.text.upper() in true_answer:
        await message.answer(f"Правильно✅\n{explanation}", reply_markup=kb.continue_or_no)
        await DB.update_data(message.from_user.id, add_correct_answer=1)
    else:
        await message.answer(f"Неправильно❌\n{explanation}", reply_markup=kb.continue_or_no)
        await DB.update_data(message.from_user.id, add_incorrect_answer=1)

#                                                                                                    hints-PRACTICE_FUNC

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

#                                                                                                                  STATS

@router.message(F.text == "Статистика")
@router.message(Command("stats"))
async def check_stats(message:Message):
    stats = await DB.select_user(message.from_user.id)
    correct_answers = stats.correct_answers
    incorrect_answers = stats.incorrect_answers
    await message.answer(f"[Cтатистика {message.from_user.first_name}]\n"
                         f"Решено задач: {correct_answers+incorrect_answers}\n"
                         f"Рейтинг: {correct_answers*15 - incorrect_answers*10}\n"
                         f"✅ Правильных ответов: {correct_answers}"
                         f"\n❌ Неправильных ответов: {incorrect_answers}")

#                                                                                                                  OTHER

@router.message(F.text)
async def any_message(message: Message):
    await message.answer("Список доступных команд:"
                         "\n"
                         "\n/password - Помогу с паролями"
                         "\n/safety_practice - Проверю твою гигиену в сети"
                         "\n/scummers_practice - Смоделирую ситуацию фишинговой атаки"
                         "\n/viruses_practice - Протестируй свои знания о вирусах"
                         "\n/stats - Посмотри свою статистику"
                         "\n\nИли /start где все функции будут представлены в виде кнопок")
