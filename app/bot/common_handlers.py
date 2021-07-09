"""
Обработчики, зависящие от типа юзера, но универсальны
"""
from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from loguru import logger

from ..db.base import session_scope
from .utils import get_or_create_user, res_dict

from .moderator_utils import send_unchecked_tasks as send_unchecked_tasks_moderator
from .moderator_utils import send_profile as send_profile_moderator

from .specialist_utils import available_tasks as available_tasks_specialist
from .specialist_utils import tasks_history as tasks_history_specialist
from .specialist_utils import tasks_current as tasks_current_specialist
from .specialist_utils import send_profile as send_profile_specialist

async def start_handler(message: types.Message):
    with session_scope() as session:
        db_user = await get_or_create_user(session, message)
        reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        if db_user.status == "moderator":
            reply_keyboard.add(KeyboardButton('Начать модерацию 📝'))
            reply_keyboard.add(KeyboardButton('Профиль 👤'))
            reply_keyboard.insert(KeyboardButton('Помощь 🙋'))
        elif db_user.status == "specialist":
            reply_keyboard.add(KeyboardButton('Список доступных задач 📝'))
            reply_keyboard.add(KeyboardButton('Текущие задачи 📋'))
            reply_keyboard.insert(KeyboardButton('История задач 📜'))
            reply_keyboard.add(KeyboardButton('Профиль 👤'))
            reply_keyboard.insert(KeyboardButton('Помощь 🙋'))
        elif db_user.status == "representative":
            reply_keyboard.add(KeyboardButton('Добавить задачу 📝'))
            reply_keyboard.add(KeyboardButton('Текущие задачи 📋'))
            reply_keyboard.insert(KeyboardButton('История задач 📜'))
            reply_keyboard.add(KeyboardButton('Профиль 👤'))
            reply_keyboard.insert(KeyboardButton('Помощь 🙋'))
        else:
            reply_keyboard.add(KeyboardButton('Зарегистрироваться 📝'))
            reply_keyboard.insert(KeyboardButton('Помощь 🙋'))
        await message.answer(res_dict["start"], parse_mode="html", reply_markup=reply_keyboard)


async def stateless_reply_handler(message: types.Message, state: FSMContext):
    """
    Все:
    Обработка сообщений из reply клавиатуры
    """
    with session_scope() as session:
        db_user = await get_or_create_user(session, message)

        command = message.text
        if command not in ["Помощь 🙋", "Начать модерацию 📝", "Список доступных задач 📝", "Текущие задачи 📋",
                           "История задач 📜", "Профиль 👤", "Добавить задачу 📝", "Зарегистрироваться 📝"]:
            await message.answer("Ошибка, команда не найдена")
        if db_user.status == "moderator":
            if command == "Помощь 🙋":
                await message.answer(res_dict["help_moderator"], parse_mode="html")
            elif command == "Начать модерацию 📝":
                await send_unchecked_tasks_moderator(session, message, state)
            elif command == "Профиль 👤":
                await send_profile_moderator(db_user, message)
        elif db_user.status == "specialist":
            if command == "Помощь 🙋":
                await message.answer(res_dict["help_specialist"], parse_mode="html")
            elif command == "Список доступных задач 📝":
                await available_tasks_specialist(db_user, message, state)
            elif command == "История задач 📜":
                await tasks_history_specialist(db_user, message, state)
            elif command == "Текущие задачи 📋":
                await tasks_current_specialist(db_user, message, state)
            elif command == "Профиль 👤":
                await send_profile_specialist(db_user, message, state)
        # elif db_user.status == "representative":
        #     if command == "Помощь 🙋":
        #         await message.answer(res_dict["help_representative"], parse_mode="html")
        #     elif command == "Добавить задачу 📝":
        #         await message.answer("Введите <b>название задачи</b>\n(не более 50 символов)", parse_mode="html",
        #                              reply_markup=representative_handler.generate_reply_keyboard_for_tasks_start())
        #         await CreateTask.name.set()
        #     elif command == "История задач 📜":
        #         await representative_handler.tasks_history(db_user, message, state)
        #     elif command == "Текущие задачи 📋":
        #         await representative_handler.tasks_current(db_user, message, state)
        #     elif command == "Профиль 👤":
        #         await representative_handler.send_profile(db_user, message, state)
        # elif db_user.status is None:
        #     if command == "Помощь 🙋":
        #         await message.answer(res_dict["help_nobody"], parse_mode="html")
        #     elif command == "Зарегистрироваться 📝":
        #         await message.answer("Введите ФИО", parse_mode="html",
        #                              reply_markup=registration.generate_inline_keyboard_for_registration_start())
        #         await Registration.fullname.set()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=['start', 'about'])
    dp.message_handler(stateless_reply_handler)


