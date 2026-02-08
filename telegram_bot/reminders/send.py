from aiogram import Bot
from database import change
from languages import get_text_by_language

async def send_notification(session, bot : Bot, telegram_id: int, db_logger, language_code: str):
    '''
    Отправляет уведомление пользователю с заданным telegram_id.
    '''

async def send_reminder(session, bot : Bot, telegram_id: int, db_logger, language_code: str):
    '''
    Отправляет напоминание пользователю с заданным telegram_id.
    '''

    db_logger.info(f"Отправка напоминания пользователю telegram_id={telegram_id}...")

    from keyboards.main import get_reminder_keyboard

    try:
        message = await bot.send_message(chat_id=telegram_id, text=get_text_by_language("reminder", language_code), reply_markup=get_reminder_keyboard())
        message_id = message.message_id
        await change.update_reminder_pending_id(session, telegram_id, message_id)
        await change.send_reminder_to_user(session, db_logger, telegram_id)
        db_logger.info(f"Напоминание пользователю telegram_id={telegram_id} успешно отправлено.")
        return True

    except Exception as e:
        db_logger.error(f"Ошибка при отправке напоминания пользователю telegram_id={telegram_id}: {e}")
        return False