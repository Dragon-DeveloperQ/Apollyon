from email.mime import message
from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from numpy import rint

from telegram_bot.keyboards.main import get_task_keyboard, task_change_cancel_keyboard, task_change_cancel_keyboard_for_description, task_change_keyboard, task_creation_keyboard1, task_creation_keyboard2, complete_task_keyboard1, complete_task_keyboard2, get_task_delete_keyboard
from telegram_bot.languages import get_commands, get_text_by_language
from database.interactions import create_task_for_character_by_telegram_id, get_all_tasks_for_character_by_telegram_id, activate_task, deactivate_task, hard_deactivate_task, reset_streaks_for_character_tasks, delete_task, change_task_name, change_task_description, get_task_by_telegram_id, get_task_by_id, accept_reminder

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
    waiting_for_task_selection_attribute = State()
    waiting_for_new_name = State()
    waiting_for_new_description = State()

class DeleteTask(StatesGroup):
    waiting_for_task_selection = State()

class CompletedTask(StatesGroup):
    waiting_for_task_selection = State()
    waiting_for_task_completion = State()


@router.message(F.text.in_(get_commands("tasks")))
@router.message(F.text.in_(get_commands("show_tasks")))
async def show_tasks_handler(message: Message, logger, language_code, telegram_id=None):
    
    if telegram_id is None:
        telegram_id = message.from_user.id
        
    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=telegram_id)
    
    if not tasks:
        await message.answer(get_text_by_language("no_tasks", language_code), reply_markup= await get_task_keyboard(language_code))
        return
    
    await reset_streaks_for_character_tasks(tasks[0].character_id)
    
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
async def show_task(message: Message, task, language_code):
    text = get_text_by_language("tasks_handler", language_code).format(
                taskname=task.title,
                description=task.description,
                difficulty=round(task.difficultyAVG,2),
                streak=task.streak)
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
    
        # Сохраняем
        await state.update_data(task_number=123)

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
async def process_task_selection_for_completion(message: Message, state: FSMContext, logger, language_code):
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
        task = await cancel_task_execution(telegram_id=message.from_user.id, task_id_by_character=task_id_by_character, state=state, message=message, logger=logger, language_code=language_code)
        logger.debug("Выполнение задания %s отменено пользователем %s", task.title, message.from_user.id)
        return
    
    if text in get_commands("complete_task"):
        task = await complete_task(telegram_id=message.from_user.id, task_id_by_character=task_id_by_character, state=state, message=message, logger=logger, language_code=language_code)
        logger.debug("Задание %s завершено пользователем %s", task.title, message.from_user.id)
        return


@router.callback_query(lambda c: c.data and c.data.startswith("reminder:"))
async def process_reminder_callback(callback_query, state: FSMContext, logger, language_code):
    
    action = callback_query.data.split(":")[1]
    data = await state.get_data()
    task_id_by_character = int(data.get("task_number"))

    if action == "continue":
        await accept_reminder(telegram_id=callback_query.from_user.id, language_code=language_code)
        await callback_query.message.delete()
        return
    
    elif action == "stop":
        task = await cancel_task_execution(telegram_id=callback_query.from_user.id, task_id_by_character=task_id_by_character, state=state, message=callback_query.message, logger=logger, language_code=language_code)
        
        await callback_query.message.edit_reply_markup(reply_markup=None)
        logger.debug("Задание %s завершено пользователем %s", task.title, callback_query.from_user.id)
        return

async def cancel_task_execution(telegram_id: int, task_id_by_character: int, state: FSMContext, message: Message=None, bot=None, logger=None, language_code=None):
    await accept_reminder(telegram_id=telegram_id, language_code=language_code)

    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=telegram_id)
    task = tasks[task_id_by_character - 1]

    await hard_deactivate_task(task.id)

    await state.clear()
    if message is None:
        await bot.send_message(telegram_id, get_text_by_language("cancel_task_execution", language_code), reply_markup= await get_task_keyboard(language_code))
    else:
        await message.reply(get_text_by_language("cancel_task_execution", language_code))
        await show_tasks_handler(message, logger, language_code, telegram_id=telegram_id)
    return task

async def complete_task(telegram_id: int, task_id_by_character: int, state: FSMContext, message: Message=None, bot=None, logger=None, language_code=None):
    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=telegram_id)
    task = tasks[task_id_by_character - 1]
        
    task_complation_stats = await deactivate_task(task_id=task.id)
        
    if task_complation_stats is None:
        if message is None:
            await bot.send_message(telegram_id, get_text_by_language("insufficient_difficulty", language_code))
        else:
            await message.answer(get_text_by_language("insufficient_difficulty", language_code))
        return

    await state.clear()

    if message is None:
        await bot.send_message(telegram_id, get_text_by_language("task_completion", language_code).format(
            difficulty=round(float(task_complation_stats["difficulty"]), 2),
            streak=task_complation_stats["streak"],
            reward=round(float(task_complation_stats["reward"]), 2)
        ))
    else:
        await message.reply(get_text_by_language("task_completion", language_code).format(
            difficulty=round(float(task_complation_stats["difficulty"]), 2),
            streak=task_complation_stats["streak"],
            reward=round(float(task_complation_stats["reward"]), 2)
        ))

    await show_tasks_handler(message, logger, language_code)
    return task

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

@router.message(ChangeTask.waiting_for_task_selection)
async def process_task_selection_for_change(message: Message, state: FSMContext, logger, language_code):
    text = (message.text or "").strip()

    if text in get_commands("cancel_task_change"):
        await state.clear()
        await message.reply(get_text_by_language("cancel_task_change", language_code))
        await show_tasks_handler(message, logger, language_code)
        return

    logger.debug("Получен номер задания для изменения от пользователя %s: %s", message.from_user.id, message.text)

    if text in get_commands("cancel_task_change"):
        await state.clear()
        await message.reply(get_text_by_language("cancel_task_change", language_code))
        await show_tasks_handler(message, logger, language_code)
        return

    if not text.isdigit():
        await message.answer(get_text_by_language("enter_valid_task_number", language_code))
        return
    
    task_number = int(text)

    tasks = await get_all_tasks_for_character_by_telegram_id(telegram_id=message.from_user.id)

    if task_number < 1 or task_number > len(tasks):
        await message.answer(get_text_by_language("enter_valid_task_number", language_code))
        return
    
    await state.update_data(task_id=tasks[task_number - 1].id)

    await state.set_state(ChangeTask.waiting_for_task_selection_attribute)
    await message.reply(get_text_by_language("what_to_change_in_task", language_code), reply_markup= await task_change_keyboard(language_code) )

@router.message(ChangeTask.waiting_for_task_selection_attribute)
async def process_task_attribute_selection(message: Message, state: FSMContext, logger, language_code):
    
    if(message.text in get_commands("cancel_task_change")):
        await state.clear()
        await message.reply(get_text_by_language("cancel_task_change", language_code))
        await show_tasks_handler(message, logger, language_code)
        return
    
    elif(message.text in get_commands("change_task_name")):
        await state.set_state(ChangeTask.waiting_for_new_name)
        await message.reply(get_text_by_language("enter_new_task_name", language_code), reply_markup=await task_change_cancel_keyboard(language_code))
    
    elif(message.text in get_commands("change_task_description")):
        await state.set_state(ChangeTask.waiting_for_new_description)
        await message.reply(get_text_by_language("enter_new_task_description", language_code), reply_markup=await task_change_cancel_keyboard_for_description(language_code))

@router.message(ChangeTask.waiting_for_new_name)
async def process_new_task_name(message: Message, state: FSMContext, logger, language_code):
    text = (message.text or "").strip()

    logger.debug("Получено новое имя задания от пользователя %s: %s", message.from_user.id, message.text)

    if text in get_commands("cancel_task_change"):
        await state.clear()
        await message.reply(get_text_by_language("cancel_task_change", language_code))
        await show_tasks_handler(message, logger, language_code)
        return
    
    if not text:
        await message.answer(get_text_by_language("new_task_name_empty", language_code))
        return

    # Проверка длины названия
    if len(text) > 100:
        await message.answer(get_text_by_language("new_task_name_too_long", language_code))
        return

    data = await state.get_data()
    task_id = data.get("task_id")

    task = await get_task_by_id(task_id)

    await change_task_name(task.id, text)

    logger.info("Задание %s изменено пользователем %s. Новое название: %s", task.title, message.from_user.id, text)

    await message.answer(get_text_by_language("task_name_changed", language_code).format(taskname=text), reply_markup= await task_change_keyboard(language_code))

    await state.set_state(ChangeTask.waiting_for_task_selection_attribute)

    task = await get_task_by_id(task_id)
    await show_task(message, task, language_code)

@router.message(ChangeTask.waiting_for_new_description)
async def process_new_task_description(message: Message, state: FSMContext, logger, language_code):
    text = (message.text or "").strip()

    if text in get_commands("cancel_task_change"):
        await state.clear()
        await message.reply(get_text_by_language("cancel_task_change", language_code))
        await show_tasks_handler(message, logger, language_code)
        return
    
    if text in get_commands("delete_description"):
        text = ""

    logger.debug("Получено новое описание задания от пользователя %s: %s", message.from_user.id, message.text)

    # Проверка длины описания
    if len(text) > 1000:
        await message.answer(get_text_by_language("new_task_description_too_long", language_code))
        return

    data = await state.get_data()
    task_id = data.get("task_id")

    task = await get_task_by_id(task_id)

    await change_task_description(task.id, text)

    logger.info("Задание %s изменено пользователем %s. Новое описание: %s", task.title, message.from_user.id, text)

    await message.answer(get_text_by_language("task_description_changed", language_code).format(taskname=task.title), reply_markup= await task_change_keyboard(language_code))

    await state.set_state(ChangeTask.waiting_for_task_selection_attribute)

    task = await get_task_by_id(task_id)
    await show_task(message, task, language_code)

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
        await delete_task(selected_task.id)
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