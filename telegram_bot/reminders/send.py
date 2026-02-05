from aiogram import Bot
from database import change
from languages import get_text_by_language

async def send_notification(session, bot : Bot, telegram_id: int, db_logger, language_code: str):
    '''
    Отправляет уведомление пользователю с заданным telegram_id.
    '''

    db_logger.info(f"Отправка уведомления пользователю telegram_id={telegram_id}...")

    try:
        await bot.send_message(chat_id=telegram_id, text=get_text_by_language("reminder", language_code))
        await change.send_notification_to_user(session, db_logger, telegram_id)
        db_logger.info(f"Уведомление пользователю telegram_id={telegram_id} успешно отправлено.")
        return True

    except Exception as e:
        db_logger.error(f"Ошибка при отправке уведомления пользователю telegram_id={telegram_id}: {e}")
        return False