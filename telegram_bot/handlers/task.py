from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram_bot.keyboards.main import get_task_keyboard, task_creation_keyboard1, task_creation_keyboard2
from telegram_bot.languages import get_commands, get_text_by_language
from database.interactions import create_task_for_character_by_telegram_id

router = Router()

class NewTask(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()


@router.message(F.text.in_(get_commands("tasks")))
async def task_handler(message: Message, logger, language_code):
    logger.debug("Демонстрация заданий пользователя %s", message.from_user.id)
    await message.answer(get_text_by_language("your_tasks", language_code), reply_markup= await get_task_keyboard(language_code))


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

    # Сбрасываем состояние
    await state.clear()

