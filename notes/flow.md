1️⃣ Пользователь нажимает "Выполнить задачу"
   
   ↓

2️⃣ MIDDLEWARE #1: logging.py
   - Логирует: "User 12345 pressed button complete_task_42"

   ↓

3️⃣ MIDDLEWARE #2: database.py
   - Создаёт DB session
   - Добавляет в контекст: data["db_session"] = session
   
   ↓

4️⃣ MIDDLEWARE #3: user_check.py
   
   - Проверяет: есть ли user в БД?
   - Если нет → "Сначала зарегистрируйся /start"
   - Если есть → продолжаем
   
   ↓

5️⃣ HANDLER: telegram_bot/handlers/tasks.py
   - Получает callback
   - Парсит task_id из callback.data
   - Вызывает: result = await core.tasks.complete_task(task_id, user_id)
   
   ↓

6️⃣ CORE: core/tasks.py
   - Высчитывает: exp, gold = core.character.calculate_task_reward(task)
   - Проверяет level up: level_up = core.character.check_level_up(...)
   - Вызывает БД: await database.crud.update_exp(user_id, exp)
   - Вызывает БД: await database.crud.update_gold(user_id, gold)
   - Вызывает БД: await database.crud.mark_task_completed(task_id)
   
   ↓

7️⃣ DATABASE: database/crud.py
   - Выполняет SQL: UPDATE user_characters SET exp = exp + 50 WHERE ...
   - Сохраняет изменения: await session.commit()
   
   ↓
    
8️⃣ Возврат в HANDLER
   - Отправляет сообщение: "✅ Задача выполнена! +50 опыта, +25 золота"