from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram_bot.keyboards.main import get_task_keyboard, task_creation_keyboard1, task_creation_keyboard2, complete_task_keyboard1, complete_task_keyboard2
from telegram_bot.languages import get_commands, get_text_by_language
from database.interactions import create_task_for_character_by_telegram_id, get_all_tasks_for_character_by_telegram_id, reward_task_completion

router = Router()

class NewTask(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()

class CompletedTask(StatesGroup):
    waiting_for_task_selection = State()
    waiting_for_task_completion = State()


@router.message(F.text.in_(get_commands("tasks")))
async def task_handler(message: Message, logger, language_code):
    logger.debug("Демонстрация заданий пользователя %s", message.from_user.id)
    await show_tasks_handler(message, logger, language_code)


@router.message(F.text.in_(get_commands("show_tasks")))
async def show_tasks_handler(message: Message, logger, language_code):
    logger.debug("Демонстрация заданий пользователя %s", message.from_user.id)
    await message.answer(get_text_by_language("your_tasks", language_code), reply_markup= await get_task_keyboard(language_code))
    
    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)
    
    '''
    Сюда добавить обработку случая, когда заданий нет
    и вернуть ответ в стиле шаблона из языкового файла
    '''
    for i in range(len(tasks)):
        if i == len(tasks) - 1:
            await message.answer(f"{i+1}) <b>{tasks[i].title}</b>\n\n{tasks[i].description}", parse_mode="HTML", reply_markup= await get_task_keyboard(language_code))
        else:
            await message.answer(f"{i+1}) <b>{tasks[i].title}</b>\n\n{tasks[i].description}", parse_mode="HTML")


'''
------------------------------------
       Создание нового задания
------------------------------------
'''
@router.message(F.text.in_(get_commands("new_task")))
async def new_task_handler(message: Message, state: FSMContext, logger, language_code):
    logger.debug("Начато создание нового задания пользователем %s", message.from_user.id)

    await state.set_state(NewTask.waiting_for_name)
    await message.reply(get_text_by_language("new_task_prompt", language_code), reply_markup= await task_creation_keyboard1(language_code))
    
@router.message(NewTask.waiting_for_name)
async def process_name(message: Message, state: FSMContext, logger, language_code):
    logger.debug("Получено имя задания от пользователя %s: %s", message.from_user.id, message.text)

    text = (message.text or "").strip()
    if not text:
        await message.answer(get_text_by_language("new_task_name_empty", language_code))
        return

    # Проверка длины названия
    if len(text) > 100:
        await message.answer(get_text_by_language("new_task_name_too_long", language_code))
        return

    if text in get_commands("cancel_task_creation"):
        await state.clear()
        await message.reply("Создание задания отменено.", reply_markup= await get_task_keyboard(language_code))
        await message.answer(get_text_by_language("your_tasks", language_code), reply_markup= await get_task_keyboard(language_code))
        return

    
    # Сохраняем имя в хранилище состояний
    await state.update_data(name=text)
    await state.set_state(NewTask.waiting_for_description)

    await message.reply(get_text_by_language("new_task_description_prompt", language_code), reply_markup= await task_creation_keyboard2(language_code))

@router.message(NewTask.waiting_for_description)
async def process_description(message: Message, state: FSMContext, logger, language_code):
    logger.debug("Получено описание задания от пользователя %s: %s", message.from_user.id, message.text)

    text = (message.text or "").strip()

    # Проверка длины описания
    if len(text) > 1000:
        await message.answer(get_text_by_language("new_task_description_too_long", language_code))
        return

    if text in get_commands("cancel_task_creation"):
        await state.clear()
        await message.reply("Создание задания отменено.", reply_markup= await get_task_keyboard(language_code))
        await message.answer(get_text_by_language("your_tasks", language_code), reply_markup= await get_task_keyboard(language_code))
        return
    
    if text in get_commands("skip_description"):
        text = ""

    # Получаем имя из хранилища состояний
    data = await state.get_data()
    name = data.get("name")

    # Создаем задание в базе данных
    await create_task_for_character_by_telegram_id(message.from_user.id, name, text)
    logger.info("Создано новое задание для пользователя %s: %s - %s", message.from_user.id, name, text)

    await message.answer(get_text_by_language("task_created_successfully", language_code), reply_markup= await get_task_keyboard(language_code))

    await show_tasks_handler(message, logger, language_code)

    # Сбрасываем состояние
    await state.clear()


'''
------------------------------------
        Выполнение задания
------------------------------------
'''
@router.message(F.text.in_(get_commands("start_task")))
async def complete_task_handler(message: Message, state: FSMContext, logger, language_code):
    logger.debug("Начато завершение задания пользователем %s", message.from_user.id)

    await state.set_state(CompletedTask.waiting_for_task_selection)
    await message.reply(get_text_by_language("enter_task_number", language_code), reply_markup= await complete_task_keyboard1(language_code))

@router.message(CompletedTask.waiting_for_task_selection)
async def process_task_selection(message: Message, state: FSMContext, logger, language_code):
    logger.debug("Получен номер задания от пользователя %s: %s", message.from_user.id, message.text)

    text = (message.text or "").strip()

    if text in get_commands("cancel_task_execution"):
        await state.clear()
        await message.reply(get_text_by_language("cancel_task_execution", language_code))
        await message.answer(get_text_by_language("your_tasks", language_code), reply_markup= await get_task_keyboard(language_code))
        return

    if not text.isdigit():
        await message.answer("Пожалуйста, введите корректный номер задания.")
        return

    task_number = int(text)
    await state.update_data(task_number=task_number)

    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)

    if task_number < 1 or task_number > len(tasks):
        await message.answer("Пожалуйста, введите корректный номер задания.")
        return

    selected_task = tasks[task_number - 1]

    logger.info("Задание %s начато пользователем %s", selected_task.title, message.from_user.id)

    '''
    --------------------------------------------------------------
            Добавить шаблон текста в языковой файл
    --------------------------------------------------------------
    '''
    await message.answer(f"Задание <b>{selected_task.title}</b> начато!", parse_mode="HTML", reply_markup= await complete_task_keyboard2(language_code))
    await state.set_state(CompletedTask.waiting_for_task_completion)

@router.message(CompletedTask.waiting_for_task_completion)
async def process_task_completion(message: Message, state: FSMContext, logger, language_code):

    text = (message.text or "").strip()
    if text in get_commands("cancel_task_execution"):
        await state.clear()
        await message.reply(get_text_by_language("cancel_task_execution", language_code))
        await message.answer(get_text_by_language("your_tasks", language_code), reply_markup= await get_task_keyboard(language_code))

        logger.debug("Выполнение задания отменено пользователем %s", message.from_user.id)
        return
    
    if text in get_commands("complete_task"):
        await message.reply(get_text_by_language("task_completion", language_code))
        await message.answer(get_text_by_language("your_tasks", language_code), reply_markup= await get_task_keyboard(language_code))

        data = await state.get_data()
        task_id_by_character = int(data.get("task_number"))

        tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)
        task = tasks[task_id_by_character - 1]

        await reward_task_completion(task_id=task.id)
        await state.clear()

        logger.debug("Задание %s завершено пользователем %s", task.title, message.from_user.id)
        return

'''
if message.text in get_commands("complete_task"):
        await state.clear()
        await message.reply(get_text_by_language("task_completion", language_code))
        await message.answer(get_text_by_language("your_tasks", language_code), reply_markup= await get_task_keyboard(language_code))
        return
'''