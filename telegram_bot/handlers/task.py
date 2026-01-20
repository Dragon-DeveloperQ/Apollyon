from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram_bot.keyboards.main import get_task_keyboard, task_creation_keyboard1, task_creation_keyboard2, complete_task_keyboard1, complete_task_keyboard2, get_task_delete_keyboard
from telegram_bot.languages import get_commands, get_text_by_language
from database.interactions import create_task_for_character_by_telegram_id, get_all_tasks_for_character_by_telegram_id, activate_task, deactivate_task, hard_deactivate_task, reset_streaks_for_character_tasks, delete_task

from datetime import datetime, timezone

from os import getenv
from dotenv import load_dotenv

load_dotenv("../config/core.env")
MAX_TASKS = int(getenv("MAX_TASKS", "20")) 

router = Router()

class NewTask(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()

class ChangeTask(StatesGroup):
    waiting_for_task_selection = State()
    waiting_for_new_name = State()
    waiting_for_new_description = State()

class DeleteTask(StatesGroup):
    waiting_for_task_selection = State()

class CompletedTask(StatesGroup):
    waiting_for_task_selection = State()
    waiting_for_task_completion = State()


@router.message(F.text.in_(get_commands("tasks")))
@router.message(F.text.in_(get_commands("show_tasks")))
async def show_tasks_handler(message: Message, logger, language_code):
    logger.debug("Демонстрация заданий пользователя %s", message.from_user.id)
    
    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)
    await reset_streaks_for_character_tasks(tasks[0].character_id)
    
    if not tasks:
        await message.answer(get_text_by_language("no_tasks", language_code), reply_markup= await get_task_keyboard(language_code))
        return
    
    await message.answer(get_text_by_language("your_tasks", language_code), reply_markup= await get_task_keyboard(language_code))
    for i in range(len(tasks)):

        text = f"{i+1}) " + get_text_by_language("tasks_handler", language_code).format(
                taskname=tasks[i].title,
                description=tasks[i].description,
                difficulty=round(tasks[i].difficultyAVG,2),
                streak=tasks[i].streak)
        
        if i == len(tasks) - 1:
            await message.answer(text, reply_markup= await get_task_keyboard(language_code))
        else:
            await message.answer(text)


'''
------------------------------------
       Создание нового задания
------------------------------------
'''
@router.message(F.text.in_(get_commands("new_task")))
async def new_task_handler(message: Message, state: FSMContext, logger, language_code):
    logger.debug("Начато создание нового задания пользователем %s", message.from_user.id)

    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)
    if len(tasks) >= MAX_TASKS:
        await message.answer(get_text_by_language("max_tasks_reached", language_code).format(max_tasks=MAX_TASKS), reply_markup= await get_task_keyboard(language_code))
        logger.info("Пользователь %s достиг максимального количества заданий", message.from_user.id)
        return

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
        await show_tasks_handler(message, logger, language_code)
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
        await show_tasks_handler(message, logger, language_code)
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

    await state.clear()


'''
------------------------------------
        Выполнение задания
------------------------------------
'''
@router.message(F.text.in_(get_commands("start_task")))
async def complete_task_handler(message: Message, state: FSMContext, logger, language_code):
    logger.debug("Начато завершение задания пользователем %s", message.from_user.id)

    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)
    if not tasks:
        await message.answer("У вас нет заданий для выполнения.", reply_markup= await get_task_keyboard(language_code))
        return
    elif len(tasks) == 1:
        selected_task = tasks[0]
        logger.info("Задание %s начато пользователем %s", selected_task.title, message.from_user.id)
        await activate_task(selected_task.id)

        await state.update_data(task_number=1)

        '''
        --------------------------------------------------------------
                Добавить шаблон текста в языковой файл
        --------------------------------------------------------------
        '''
        await message.answer(f"Задание <b>{selected_task.title}</b> начато!", parse_mode="HTML", reply_markup= await complete_task_keyboard2(language_code))
        await state.set_state(CompletedTask.waiting_for_task_completion)
        return

    await state.set_state(CompletedTask.waiting_for_task_selection)
    await message.reply(get_text_by_language("enter_task_number", language_code), reply_markup= await complete_task_keyboard1(language_code))

@router.message(CompletedTask.waiting_for_task_selection)
async def process_task_selection(message: Message, state: FSMContext, logger, language_code):
    logger.debug("Получен номер задания от пользователя %s: %s", message.from_user.id, message.text)

    text = (message.text or "").strip()

    if text in get_commands("cancel_task_execution"):
        await state.clear()
        await message.reply(get_text_by_language("cancel_task_execution", language_code))
        await show_tasks_handler(message, logger, language_code)
        return

    if not text.isdigit():
        await message.answer(get_text_by_language("enter_valid_task_number", language_code))
        return

    task_number = int(text)
    await state.update_data(task_number=task_number)

    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)

    if task_number < 1 or task_number > len(tasks):
        await message.answer(get_text_by_language("enter_valid_task_number", language_code))
        return

    selected_task = tasks[task_number - 1]
    await activate_task(selected_task.id)

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
    data = await state.get_data()
    task_id_by_character = int(data.get("task_number"))
    
    if text in get_commands("cancel_task_execution"):
        tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)
        task = tasks[task_id_by_character - 1]

        await hard_deactivate_task(task.id)

        await state.clear()
        await message.reply(get_text_by_language("cancel_task_execution", language_code))
        await show_tasks_handler(message, logger, language_code)

        logger.debug("Выполнение задания отменено пользователем %s", message.from_user.id)
        return
    
    if text in get_commands("complete_task"):
        tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)
        task = tasks[task_id_by_character - 1]
        
        task_complation_stats = await deactivate_task(task_id=task.id)
        
        if task_complation_stats is None:
            await message.answer(get_text_by_language("insufficient_difficulty", language_code))
            return

        await state.clear()

        await message.reply(get_text_by_language("task_completion", language_code).format(
            difficulty=round(float(task_complation_stats["difficulty"]), 2),
            streak=task_complation_stats["streak"],
            reward=round(float(task_complation_stats["reward"]), 2)
        ))

        await show_tasks_handler(message, logger, language_code)

        logger.debug("Задание %s завершено пользователем %s", task.title, message.from_user.id)
        return


'''
------------------------------------
        Изменение задания
------------------------------------
'''
@router.message(F.text.in_(get_commands("change_task")))
async def change_task_handler(message: Message, state: FSMContext, logger, language_code):
    logger.debug("Начато изменение задания пользователем %s", message.from_user.id)

    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)
    if not tasks:
        await message.answer(get_text_by_language("no_tasks", language_code), reply_markup= await get_task_keyboard(language_code))
        return

    await state.set_state(ChangeTask.waiting_for_task_selection)
    await message.reply(get_text_by_language("enter_task_number", language_code), reply_markup= await get_task_delete_keyboard(language_code))


'''
------------------------------------
        Удаление задания
------------------------------------
'''

@router.message(F.text.in_(get_commands("delete_task")))
async def delete_task_handler(message: Message, state: FSMContext, logger, language_code):
    logger.debug("Начато удаление задания пользователем %s", message.from_user.id)

    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)
    if not tasks:
        await message.answer(get_text_by_language("no_tasks", language_code), reply_markup= await get_task_keyboard(language_code))
        return
    elif len(tasks) == 1:
        selected_task = tasks[0]
        await message.answer(get_text_by_language("task_deleted", language_code).format(taskname=selected_task.title), reply_markup= await get_task_keyboard(language_code))
        await hard_deactivate_task(selected_task.id)
        logger.info("Задание %s удалено пользователем %s", selected_task.title, message.from_user.id)
        await show_tasks_handler(message, logger, language_code)
        return

    await state.set_state(DeleteTask.waiting_for_task_selection)
    await message.reply(get_text_by_language("enter_task_number", language_code), reply_markup= await get_task_delete_keyboard(language_code))

@router.message(DeleteTask.waiting_for_task_selection)
async def process_task_deletion(message: Message, state: FSMContext, logger, language_code):
    logger.debug("Получен номер задания для удаления от пользователя %s: %s", message.from_user.id, message.text)

    text = (message.text or "").strip()

    if text in get_commands("cancel_task_deletion"):
        await state.clear()
        await message.reply(get_text_by_language("cancel_task_deletion", language_code))
        await show_tasks_handler(message, logger, language_code)
        return

    if not text.isdigit():
        await message.answer(get_text_by_language("enter_valid_task_number", language_code))
        return

    task_number = int(text)
    await state.update_data(task_number=task_number)

    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)

    if task_number < 1 or task_number > len(tasks):
        await message.answer(get_text_by_language("enter_valid_task_number", language_code))
        return

    selected_task = tasks[task_number - 1]
    await delete_task(selected_task.id)

    logger.info("Задание %s удалено пользователем %s", selected_task.title, message.from_user.id)

    await message.answer(get_text_by_language("task_deleted", language_code).format(taskname=selected_task.title), reply_markup= await get_task_keyboard(language_code))

    await show_tasks_handler(message, logger, language_code)

    await state.clear()