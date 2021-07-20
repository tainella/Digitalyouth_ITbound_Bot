from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from loguru import logger

from ..core.settings import Settings
from .handlers.general_handlers import register_handlers as register_handlers_general
from .handlers.common_handlers import register_handlers as register_handlers_common
from .handlers.representative_handler import register_handlers as register_handlers_representative
from .handlers.registration_handlers import register_handlers as register_handlers_registration




#
# # Модератор
# # TODO а где модератор?!
# # Конец Модератора
#
#
# # Конец колбеков для регистрации
# # Блок обработки колбеков от всех
# @dp.callback_query_handler(state='*')
# async def some_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
#     """
#     Всеget_state
#     Обработка колбеков без КА
#     """
#     db_user = db_worker.get_user(callback_query.from_user.id)
#     if not db_user:
#         db_user = db_worker.add_user(callback_query.from_user.id, callback_query.from_user.full_name,
#                                      callback_query.from_user.username)
#     data = callback_query.data.split()
#     command = data[0]
#     to_answer = 'Кнопка устарела, либо ещё не работает, начните заного:('
#     if db_user.status == "representative":
#         if command == "cp_tasks":
#             async with state.proxy() as state_data:
#                 if f'tasks_{data[2]}' in state_data:
#                     to_answer = ''
#                     if data[2] == 'history' and callback_query.message.text != "История задач, которые Вы добавляли. " \
#                                                                                "\nЧтобы получить больше информации, " \
#                                                                                "нажмите на задачу.":
#                         await callback_query.message.edit_text('История задач, которые Вы добавляли. '
#                                                                '\nЧтобы получить больше информации, нажмите на задачу.')
#                     if data[2] == 'current' and callback_query.message.text != "Текущие задачи, которые Вы добавляли." \
#                                                                                " \nЧтобы получить больше информации и" \
#                                                                                " редактировать, нажмите на задачу.":
#                         await callback_query.message.edit_text('Текущие задачи, которые Вы добавляли. \nЧтобы получить'
#                                                                ' больше информации и редактировать, нажмите на задачу.')
#                     await callback_query.message.edit_reply_markup(reply_markup=await
#                             representative_handler.generate_inline_keyboard_for_tasks(state, int(data[1]), data[2]))
#                 else:
#                     to_answer = 'Кнопка устарела, начните заного'
#         elif command == "task_info":
#             to_answer = ''
#             keyboard = InlineKeyboardMarkup()
#             if data[3] == "history":
#                 keyboard.insert(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} history'))
#             if data[3] == "current":
#                 keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} current'))
#                 keyboard.insert(InlineKeyboardButton('Редактировать', callback_data=f'edit_task {data[1]}'))
#                 keyboard.insert(InlineKeyboardButton('Удалить', callback_data=f'delete_task_repr {data[1]} {data[2]}'))
#             await callback_query.message.edit_text(
#                 text=utils.generate_task_description(db_worker.get_task(int(data[1]))), parse_mode="html")
#             await callback_query.message.edit_reply_markup(reply_markup=keyboard)
#         elif command == "delete_task_repr":
#             to_answer = 'Подтвердите удаление задания'
#             keyboard = InlineKeyboardMarkup()
#             keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} current'))
#             keyboard.insert(InlineKeyboardButton('Редактировать', callback_data=f'edit_task {data[1]}'))
#             keyboard.insert(
#                 InlineKeyboardButton('Удалить!', callback_data=f'delete_task_repr_sure {data[1]} {data[2]}'))
#             await callback_query.message.edit_reply_markup(reply_markup=keyboard)
#         elif command == "delete_task_repr_sure":
#             db_worker.get_task(int(data[1])).status = "canceled_by_represented"
#             db_worker.Session.commit()
#             tasks = db_worker.get_tasks_for_user(db_user, ['awaiting_confirmation', 'awaiting_specialist', 'in_work'])
#             async with state.proxy() as state_data:
#                 state_data['tasks_current'] = tasks
#             to_answer = 'Задание было успешно удалено!'
#             await callback_query.message.edit_text(
#                 'Текущие задачи, которые Вы добавляли. \nЧтобы получить больше информации и редактировать, нажмите на задачу.')
#             await callback_query.message.edit_reply_markup(
#                 reply_markup=await representative_handler.generate_inline_keyboard_for_tasks(state, int(data[2]),
#                                                                                              'current'))
#     elif db_user.status == "specialist":
#         if command == "cp_tasks":
#             async with state.proxy() as state_data:
#                 if f'tasks_{data[2]}' in state_data:
#                     to_answer = ''
#                     if data[
#                         2] == 'history' and callback_query.message.text != "История задач, которые Вы выполнили. \nЧтобы получить больше информации, нажмите на задачу.":
#                         await callback_query.message.edit_text(
#                             'История задач, которые Вы выполнили. \nЧтобы получить больше информации, нажмите на задачу.')
#                     if data[
#                         2] == 'current' and callback_query.message.text != "Текущие задачи, которые Вы сейчас выполняете. \nЧтобы получить больше информации и редактировать, нажмите на задачу.":
#                         await callback_query.message.edit_text(
#                             'Текущие задачи, которые Вы сейчас выполняете. \nЧтобы получить больше информации и редактировать, нажмите на задачу.')
#                     if data[
#                         2] == 'available' and callback_query.message.text != "Доступные на взятие задачи. \nЧтобы получить больше информации, нажмите на задачу.":
#                         await callback_query.message.edit_text(
#                             'Доступные на взятие задачи. \nЧтобы получить больше информации, нажмите на задачу.')
#                     await callback_query.message.edit_reply_markup(
#                         reply_markup=await representative_handler.generate_inline_keyboard_for_tasks(state,
#                                                                                                      int(data[1]),
#                                                                                                      data[2]))
#                 else:
#                     to_answer = 'Кнопка устарела, начните заного'
#         elif command == "task_info":
#             to_answer = ''
#             keyboard = InlineKeyboardMarkup()
#             if data[3] == "history":
#                 keyboard.insert(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} history'))
#             elif data[3] == "current":
#                 keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} current'))
#                 keyboard.insert(
#                     InlineKeyboardButton('Отказаться от выполнения', callback_data=f'refuse_task {data[1]} {data[2]}'))
#             elif data[3] == "available":
#                 keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} available'))
#                 keyboard.insert(InlineKeyboardButton('Взять', callback_data=f'take_task {data[1]} {data[2]}'))
#             await callback_query.message.edit_text(
#                 text=utils.generate_task_description(db_worker.get_task(int(data[1]))), parse_mode="html")
#             await callback_query.message.edit_reply_markup(reply_markup=keyboard)
#         elif command == "refuse_task":
#             to_answer = 'Подтвердите отказ от выполнения'
#             keyboard = InlineKeyboardMarkup()
#             keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} current'))
#             keyboard.insert(InlineKeyboardButton('Отказаться от выполнения!',
#                                                  callback_data=f'refuse_task_sure {data[1]} {data[2]}'))
#             await callback_query.message.edit_reply_markup(reply_markup=keyboard)
#         elif command == "refuse_task_sure":
#             task = db_worker.get_task(int(data[1]))
#             task.status = "awaiting_specialist"
#             task.specialist = None
#             # TODO уведомить как-то представителя
#             db_worker.Session.commit()
#             tasks = db_worker.get_tasks_for_user(db_user, ['awaiting_confirmation', 'awaiting_specialist', 'in_work'])
#             async with state.proxy() as state_data:
#                 state_data['tasks_current'] = tasks
#             to_answer = 'Вы успешно отказались от задания!'
#             await callback_query.message.edit_text(
#                 'Текущие задачи, которые Вы сейчас выполняете. \nЧтобы получить больше информации и редактировать, нажмите на задачу.')
#             await callback_query.message.edit_reply_markup(
#                 reply_markup=await representative_handler.generate_inline_keyboard_for_tasks(state, int(data[2]),
#                                                                                              'current'))
#         elif command == "take_task":
#             to_answer = 'Подтвердите взятие задачи'
#             keyboard = InlineKeyboardMarkup()
#             keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} current'))
#             keyboard.insert(InlineKeyboardButton('Взять!', callback_data=f'take_task_sure {data[1]} {data[2]}'))
#             await callback_query.message.edit_reply_markup(reply_markup=keyboard)
#         elif command == "take_task_sure":
#             db_user = db_worker.get_user(callback_query.from_user.id)
#             task = db_worker.get_task(int(data[1]))
#             task.status = "in_work"
#             task.specialist = db_user.specialist
#             # TODO уведомить как-то представителя
#             db_worker.Session.commit()
#             tasks = db_worker.get_opened_tasks([sphere.spheres for sphere in db_user.specialist.spheres])
#             async with state.proxy() as state_data:
#                 state_data['tasks_available'] = tasks
#             to_answer = 'Вы успешно взяли задание'
#             await callback_query.message.edit_text(
#                 'Доступные на взятие задачи. \nЧтобы получить больше информации, нажмите на задачу.')
#             await callback_query.message.edit_reply_markup(
#                 reply_markup=await representative_handler.generate_inline_keyboard_for_tasks(state, int(data[2]),
#                                                                                              'available'))
#     elif db_user.status == "moderator":
#         if command == "cp_tasks":
#             async with state.proxy() as state_data:
#                 if f'tasks_{data[2]}' in state_data:
#                     to_answer = ''
#                     if data[
#                         2] == 'unchecked' and callback_query.message.text != "Задачи, требующие модерацию. \nЧтобы получить больше информации и редактировать, нажмите на задачу.":
#                         await callback_query.message.edit_text(
#                             'Задачи, требующие модерацию. \nЧтобы получить больше информации и редактировать, нажмите на задачу.')
#                     await callback_query.message.edit_reply_markup(
#                         reply_markup=await representative_handler.generate_inline_keyboard_for_tasks(state,
#                                                                                                      int(data[1]),
#                                                                                                      data[2]))
#                 else:
#                     to_answer = 'Кнопка устарела, начните заного'
#         elif command == "task_info":
#             to_answer = ''
#             keyboard = InlineKeyboardMarkup()
#             if data[3] == "unchecked":
#                 keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} available'))
#                 keyboard.insert(
#                     InlineKeyboardButton('Отметить как подтверждённое', callback_data=f'confirm {data[1]} {data[2]}'))
#             await callback_query.message.edit_text(
#                 text=utils.generate_task_description(db_worker.get_task(int(data[1]))), parse_mode="html")
#             await callback_query.message.edit_reply_markup(reply_markup=keyboard)
#         elif command == "confirm":
#             db_user = db_worker.get_user(callback_query.from_user.id)
#             task = db_worker.get_task(int(data[1]))
#             task.status = "awaiting_specialist"
#             # task.specialist = db_user.specialist
#             # TODO уведомить специалистов
#             db_worker.Session.commit()
#             tasks = db_worker.get_unchecked_taskes()
#             async with state.proxy() as state_data:
#                 state_data['tasks_unchecked'] = tasks
#             to_answer = 'Вы отметили задание, как прошедшее модерацию'
#             await callback_query.message.edit_text(
#                 'Задачи, требующие модерацию. \nЧтобы получить больше информации и редактировать, нажмите на задачу.')
#             await callback_query.message.edit_reply_markup(
#                 reply_markup=await moderator_handler.generate_inline_keyboard_for_tasks(state, int(data[2]),
#                                                                                         'unchecked'))
#
#     await callback_query.answer(to_answer)
#     if to_answer == "Ошибка, начните заного":
#         logging.warning(f"Необработанный колбек \"{callback_query.data}\", состояние: {await state.get_state()}")
#

if __name__ == '__main__':
    bot = Bot(token=Settings().telegram_api)
    # TODO перейти на redis storage
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    register_handlers_general(dp)
    register_handlers_common(dp)
    register_handlers_representative(dp)
    register_handlers_registration(dp)

    logger.info("Bot started!")
    executor.start_polling(dp, skip_updates=True)
