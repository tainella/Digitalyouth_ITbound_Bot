import logging
import configparser
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

import utils
import db_worker
from ..core.settings import Settings
import specialist_handler, representative_handler, moderator_handler, registration
from utils import res_dict

BASE = Path(os.path.realpath(__file__))
os.chdir(BASE.parent)


bot = Bot(token=Settings().telegram_api)
storage = MemoryStorage()  # TODO перейти на redis storage
dp = Dispatcher(bot, storage=storage)


class CreateTask(StatesGroup):
    """
    КА создания задачи для создания таска представителем
    """
    name = State()
    description = State()
    spheres = State()
    done = State()


class Registration(StatesGroup):
    """
    КА создания задачи для регистрации
    """
    fullname = State()
    phone = State()
    wished_role = State()
    done = State()


def get_status(chat_id: int):
    # TODO получать статус из бд
    return "representative"


# Блок обработчиков общий(Все)

@dp.message_handler(commands="start", state=None)
async def send(message: types.Message):
    """
    Все:
    Сообщение приветствия + генерация reply клавы
    """
    db_user = db_worker.get_user(message.from_user.id)
    if not db_user:
        db_user = db_worker.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    # logging.info(db_user)
    reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    # TODO добавить эмодзи
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
    # print(message.from_user.get_mention(as_html=True))


# TODO нормальное info
@dp.message_handler(commands="info", state=None)
async def send(message: types.Message):
    await message.answer(res_dict["info"], parse_mode="html")


# TODO нормальное contacts
@dp.message_handler(commands="contacts", state=None)
async def send(message: types.Message):
    await message.answer(res_dict["contacts"], parse_mode="html")


@dp.message_handler(state='*', commands='/cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Все:
    Отмена действий через команду или сообщение
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer('<i>Отменено.</i>', parse_mode="html")


@dp.callback_query_handler(lambda callback_query: callback_query.data == "cancel", state='*')
async def some_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Все:
    Отмена действий через inline клавиатуру
    """
    current_state = await state.get_state()
    if current_state is None:
        await callback_query.answer('Вы и так ничего не делаете:)')
    else:
        await state.finish()
        await callback_query.message.delete()
        await callback_query.message.answer('Отменено')
        await callback_query.answer()


@dp.message_handler(state=None)
async def send(message: types.Message, state: FSMContext):
    """
    Все:
    Обработка сообщений из reply клавиатуры
    """
    db_user = db_worker.get_user(message.from_user.id)
    if not db_user:
        db_user = db_worker.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    command = message.text
    if command not in ["Помощь 🙋", "Начать модерацию 📝", "Список доступных задач 📝", "Текущие задачи 📋",
                       "История задач 📜", "Профиль 👤", "Добавить задачу 📝", "Зарегистрироваться 📝"]:
        await message.answer("Ошибка, команда не найдена")
    if db_user.status == "moderator":
        if command == "Помощь 🙋":
            await message.answer(res_dict["help_moderator"], parse_mode="html")
        elif command == "Начать модерацию 📝":
            unchecked_taskes = db_worker.get_unchecked_taskes()
            await moderator_handler.send_unchecked_taskes(db_user, unchecked_taskes, message, state)
        elif command == "Профиль 👤":
            await moderator_handler.send_profile(db_user, message, state)
    elif db_user.status == "specialist":
        if command == "Помощь 🙋":
            await message.answer(res_dict["help_specialist"], parse_mode="html")
        elif command == "Список доступных задач 📝":
            await specialist_handler.available_tasks(db_user, message, state)
        elif command == "История задач 📜":
            await specialist_handler.tasks_history(db_user, message, state)
        elif command == "Текущие задачи 📋":
            await specialist_handler.tasks_current(db_user, message, state)
        elif command == "Профиль 👤":
            await specialist_handler.send_profile(db_user, message, state)
    elif db_user.status == "representative":
        if command == "Помощь 🙋":
            await message.answer(res_dict["help_representative"], parse_mode="html")
        elif command == "Добавить задачу 📝":
            await message.answer("Введите <b>название задачи</b>\n(не более 50 символов)", parse_mode="html",
                                 reply_markup=representative_handler.generate_reply_keyboard_for_tasks_start())
            await CreateTask.name.set()
        elif command == "История задач 📜":
            await representative_handler.tasks_history(db_user, message, state)
        elif command == "Текущие задачи 📋":
            await representative_handler.tasks_current(db_user, message, state)
        elif command == "Профиль 👤":
            await representative_handler.send_profile(db_user, message, state)
    elif db_user.status == None:
        if command == "Помощь 🙋":
            await message.answer(res_dict["help_nobody"], parse_mode="html")
        elif command == "Зарегистрироваться 📝":
            await message.answer("Введите ФИО", parse_mode="html",
                                 reply_markup=registration.generate_inline_keyboard_for_registration_start())
            await Registration.fullname.set()


# Конец блока для всех
# Блок обработки Представителя

@dp.callback_query_handler(lambda callback_query: callback_query.data == "done", state=CreateTask.spheres)
async def some_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Представитель:
    Подтверждение правильности введённых данных задачи
    """
    async with state.proxy() as data:
        to_return = f"Подтвердите правильность составленной задачи\n<i>Название:</i>\n{data['name']}\n\n"
        to_return += f"<i>Описание:</i>\n{data['description']}\n\n"
        to_return += f"<i>Сферы разработки:</i>\n{', '.join(filter(lambda x: data['spheres'][x], data['spheres']))}"
    await callback_query.message.edit_text(to_return, parse_mode="html")
    await callback_query.message.edit_reply_markup(
        reply_markup=representative_handler.generate_reply_keyboard_for_tasks_done())
    await CreateTask.next()
    await callback_query.answer()


@dp.callback_query_handler(lambda callback_query: callback_query.data == "done", state=CreateTask.done)
async def some_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Представитель:
    Отправка данных задачи на модерацию
    """
    async with state.proxy() as data:
        data['spheres'] = list(filter(lambda x: data['spheres'][x], data['spheres']))
        await callback_query.message.answer(f'Задание <i>"{data["name"]}"</i> было отправлено на проверку модератору.',
                                            parse_mode="html")
        # TODO отсылать в БД
        db_worker.add_task(data['name'], data['description'],
                           db_worker.get_user(callback_query.from_user.id).representative, data['spheres'])
        await callback_query.answer()
    await state.finish()


@dp.callback_query_handler(lambda callback_query: callback_query.data != "back", state=CreateTask.spheres)
async def some_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Представитель:
    Выбор сфер разработки задачи
    """
    async with state.proxy() as data:
        data['spheres'][callback_query.data] = not data['spheres'][callback_query.data]
    await callback_query.message.edit_reply_markup(
        await representative_handler.generate_reply_keyboard_for_tasks_spheres(state))
    await callback_query.answer()


@dp.callback_query_handler(lambda callback_query: callback_query.data == "back", state=CreateTask.description)
async def send(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Представитель:
    Выбор названия задачи
    """
    await callback_query.answer()
    await callback_query.message.delete()
    await CreateTask.name.set()
    await callback_query.message.answer("Введите <b>название задачи</b>\n(не более 50 символов)", parse_mode="html",
                                        reply_markup=representative_handler.generate_reply_keyboard_for_tasks_start())


@dp.callback_query_handler(lambda callback_query: callback_query.data == "back", state=CreateTask.spheres)
@dp.message_handler(state=CreateTask.name)
async def send(update, state: FSMContext):
    """
    Представитель:
    Выбор описания задачи иы обработка неправильного названия
    """
    if isinstance(update, types.CallbackQuery):
        message = update.message
        await update.answer()
        await update.message.delete()
        await CreateTask.description.set()
        await message.answer("Введите <b>описание задачи</b>\n(не более 2000 символов)", parse_mode="html",
                             reply_markup=representative_handler.generate_reply_keyboard_for_tasks())
    else:
        message = update
        if len(message.text) > 50:
            await message.answer(
                f"Ошибка, название должно быть не более 50 символов.\n(Введено {len(message.text)} символов)\n\nВведите <b>другое название задачи</b>\n(не более 50 символов)",
                parse_mode="html", reply_markup=utils.generate_reply_keyboard_for_tasks_start())
        elif message.text in ["Помощь", "Добавить задачу", "История задач", "Текущие задачи"]:
            await message.answer(
                'Ошибка, неправильное название.\n\nВведите <b>другое название задачи</b>\n(не более 50 символов)\nДля отмены создания задания, нажмите <code>"Отмена"</code>',
                parse_mode="html", reply_markup=utils.generate_reply_keyboard_for_tasks_start())
        else:
            async with state.proxy() as data:
                data['name'] = message.text

            await CreateTask.next()
            await message.answer("Введите <b>описание задачи</b>\n(не более 2000 символов)", parse_mode="html",
                                 reply_markup=representative_handler.generate_reply_keyboard_for_tasks())


@dp.callback_query_handler(lambda callback_query: callback_query.data == "back", state=CreateTask.done)
@dp.message_handler(state=CreateTask.description)
async def send(update, state: FSMContext):
    """
    Представитель:
    Выбор сферы разработки и обработка неправильного описания
    """
    if isinstance(update, types.CallbackQuery):
        message = update.message
        await update.answer()
        await update.message.delete()
        await CreateTask.spheres.set()
        await message.answer("Выберите сферы разработки",
                             reply_markup=await representative_handler.generate_reply_keyboard_for_tasks_spheres(state))
    else:
        message = update
        if len(message.text) > 2000:
            await message.answer(
                "Ошибка, описание должно быть не более 2000 символов.\n(Введено {len(message.text)} символов)\n\nВведите <b>другое описание задачи</b>\n(не более 3000 символов)",
                parse_mode="html", reply_markup=representative_handler.generate_reply_keyboard_for_tasks())
        elif message.text in ["Помощь", "Добавить задачу", "История задач", "Текущие задачи"]:
            await message.answer(
                'Ошибка, неправильное описание.\n\nВведите <b>другое описание задачи</b>\n(не более 2000 символов)\nДля отмены создания задания, нажмите <code>"Отмена"</code>',
                parse_mode="html", reply_markup=representative_handler.generate_reply_keyboard_for_tasks())
        else:
            async with state.proxy() as data:
                data['description'] = message.text
                data['spheres'] = {interest: False for interest in db_worker.get_all_interests()}

            await CreateTask.next()
            await message.answer("Выберите сферы разработки",
                                 reply_markup=await representative_handler.generate_reply_keyboard_for_tasks_spheres(
                                     state))


# Конец блока Представителя

# Модератор

# Конец Модератора

# Колбеки для регистрации
@dp.callback_query_handler(lambda callback_query: callback_query.data == "back", state=Registration.phone)
async def send(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Представитель:
    Выбор названия задачи
    """
    await callback_query.answer()
    await callback_query.message.delete()
    await Registration.fullname.set()
    await callback_query.message.answer("Введите ФИО", parse_mode="html",
                                        reply_markup=registration.generate_inline_keyboard_for_registration_start())


@dp.callback_query_handler(lambda callback_query: callback_query.data == "back", state=Registration.wished_role)
@dp.message_handler(state=Registration.fullname)
async def send(update, state: FSMContext):
    """
        Регистрация:
        Ввели фамилию, ввод телефона
        """
    if isinstance(update, types.CallbackQuery):
        message = update.message
        await update.answer()
        await update.message.delete()
        await Registration.phone.set()
        await message.answer("Введите <b>свой телефонный номер</b>\n", parse_mode="html",
                             reply_markup=representative_handler.generate_reply_keyboard_for_tasks())
    else:
        message = update
        if len(message.text) > 50:
            await message.answer(
                f"Ошибка, ФИО должно быть не более 50 символов.\n(Введено {len(message.text)} символов)\n\nВведите <b>укороченную версию ФИО</b>\n(не более 50 символов)",
                parse_mode="html", reply_markup=utils.generate_reply_keyboard_for_tasks_start())
        elif message.text in ["Помощь", "Регистрация"]:
            await message.answer(
                'Ошибка, неправильное ФИО.\n\nВведите <b>настоящее ФИО</b>\n(не более 50 символов)\nДля отмены регистрации нажмите <code>"Отмена"</code>',
                parse_mode="html", reply_markup=utils.generate_reply_keyboard_for_tasks_start())
        else:
            async with state.proxy() as data:
                data['fullname'] = message.text

            await Registration.next()
            await message.answer("Введите <b>свой телефонный номер</b>\n", parse_mode="html",
                                 reply_markup=representative_handler.generate_reply_keyboard_for_tasks())


@dp.callback_query_handler(lambda callback_query: callback_query.data == "back", state=Registration.done)
@dp.message_handler(state=Registration.phone)
async def send(update, state: FSMContext):
    """
        Регистрация:
        Обработка телефона и выбор желаемой роли
        """
    if isinstance(update, types.CallbackQuery):
        message = update.message
        await update.answer()
        await update.message.delete()
        await Registration.wished_role.set()
        await message.answer("Кто вы?", reply_markup=await registration.generate_role_keyboard())
    else:
        message = update
        # добавить проверку телефона
        if message.text in ["Помощь", "Регистрация"]:
            await message.answer(
                'Ошибка, неправильный телефонный номер.\n\nВведите <b>другой телефонный номер</b>\nДля отмены регистрации, нажмите <code>"Отмена"</code>',
                parse_mode="html", reply_markup=representative_handler.generate_reply_keyboard_for_tasks())
        else:
            async with state.proxy() as data:
                data['phone'] = message.text
            await Registration.next()
            await message.answer("Кто Вы?", reply_markup=registration.generate_role_keyboard())


@dp.callback_query_handler(state=Registration.wished_role)
async def send(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Регистрация:
    Отправка анкеты и данных
    """
    user = db_worker.get_user(callback_query.from_user.id)
    if callback_query.data == 'wish_specialist':
        db_worker.add_specialist(user)
        user.status = "specialist"
        await callback_query.message.answer("Регистрация прошла успешно")
        reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        reply_keyboard.add(KeyboardButton('Список доступных задач'))
        reply_keyboard.add(KeyboardButton('Текущие задачи'))
        reply_keyboard.insert(KeyboardButton('История задач'))
        # reply_keyboard.add(KeyboardButton('Настройки')) 
        reply_keyboard.add(KeyboardButton('Профиль'))
        reply_keyboard.insert(KeyboardButton('Помощь'))
        await callback_query.message.answer(res_dict["start"], parse_mode="html", reply_markup=reply_keyboard)
    else:
        if callback_query.data == 'wish_moderator':
            user.status = "wish_moder"
        else:
            user.status = "wish_repre"
        await callback_query.message.answer("Ваша анкета была отправлена на рассмотрение модератором")
    async with state.proxy() as data:
        user.real_fullname = data['fullname']
        user.phone = data['phone']
    db_worker.Session.commit()
    await callback_query.answer()
    await state.finish()


# Конец колбеков для регистрации
# Блок обработки колбеков от всех 
@dp.callback_query_handler(state='*')
async def some_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Всеget_state
    Обработка колбеков без КА
    """
    db_user = db_worker.get_user(callback_query.from_user.id)
    if not db_user:
        db_user = db_worker.add_user(callback_query.from_user.id, callback_query.from_user.full_name,
                                     callback_query.from_user.username)
    data = callback_query.data.split()
    command = data[0]
    to_answer = 'Кнопка устарела, либо ещё не работает, начните заного:('
    if db_user.status == "representative":
        if command == "cp_tasks":
            async with state.proxy() as state_data:
                if f'tasks_{data[2]}' in state_data:
                    to_answer = ''
                    if data[
                        2] == 'history' and callback_query.message.text != "История задач, которые Вы добавляли. \nЧтобы получить больше информации, нажмите на задачу.":
                        await callback_query.message.edit_text(
                            'История задач, которые Вы добавляли. \nЧтобы получить больше информации, нажмите на задачу.')
                    if data[
                        2] == 'current' and callback_query.message.text != "Текущие задачи, которые Вы добавляли. \nЧтобы получить больше информации и редактировать, нажмите на задачу.":
                        await callback_query.message.edit_text(
                            'Текущие задачи, которые Вы добавляли. \nЧтобы получить больше информации и редактировать, нажмите на задачу.')
                    await callback_query.message.edit_reply_markup(
                        reply_markup=await representative_handler.generate_inline_keyboard_for_tasks(state,
                                                                                                     int(data[1]),
                                                                                                     data[2]))
                else:
                    to_answer = 'Кнопка устарела, начните заного'
        elif command == "task_info":
            to_answer = ''
            keyboard = InlineKeyboardMarkup()
            if data[3] == "history":
                keyboard.insert(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} history'))
            if data[3] == "current":
                keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} current'))
                keyboard.insert(InlineKeyboardButton('Редактировать', callback_data=f'edit_task {data[1]}'))
                keyboard.insert(InlineKeyboardButton('Удалить', callback_data=f'delete_task_repr {data[1]} {data[2]}'))
            await callback_query.message.edit_text(
                text=utils.generate_task_description(db_worker.get_task(int(data[1]))), parse_mode="html")
            await callback_query.message.edit_reply_markup(reply_markup=keyboard)
        elif command == "delete_task_repr":
            to_answer = 'Подтвердите удаление задания'
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} current'))
            keyboard.insert(InlineKeyboardButton('Редактировать', callback_data=f'edit_task {data[1]}'))
            keyboard.insert(
                InlineKeyboardButton('Удалить!', callback_data=f'delete_task_repr_sure {data[1]} {data[2]}'))
            await callback_query.message.edit_reply_markup(reply_markup=keyboard)
        elif command == "delete_task_repr_sure":
            db_worker.get_task(int(data[1])).status = "canceled_by_represented"
            db_worker.Session.commit()
            tasks = db_worker.get_tasks_for_user(db_user, ['awaiting_confirmation', 'awaiting_specialist', 'in_work'])
            async with state.proxy() as state_data:
                state_data['tasks_current'] = tasks
            to_answer = 'Задание было успешно удалено!'
            await callback_query.message.edit_text(
                'Текущие задачи, которые Вы добавляли. \nЧтобы получить больше информации и редактировать, нажмите на задачу.')
            await callback_query.message.edit_reply_markup(
                reply_markup=await representative_handler.generate_inline_keyboard_for_tasks(state, int(data[2]),
                                                                                             'current'))
    elif db_user.status == "specialist":
        if command == "cp_tasks":
            async with state.proxy() as state_data:
                if f'tasks_{data[2]}' in state_data:
                    to_answer = ''
                    if data[
                        2] == 'history' and callback_query.message.text != "История задач, которые Вы выполнили. \nЧтобы получить больше информации, нажмите на задачу.":
                        await callback_query.message.edit_text(
                            'История задач, которые Вы выполнили. \nЧтобы получить больше информации, нажмите на задачу.')
                    if data[
                        2] == 'current' and callback_query.message.text != "Текущие задачи, которые Вы сейчас выполняете. \nЧтобы получить больше информации и редактировать, нажмите на задачу.":
                        await callback_query.message.edit_text(
                            'Текущие задачи, которые Вы сейчас выполняете. \nЧтобы получить больше информации и редактировать, нажмите на задачу.')
                    if data[
                        2] == 'available' and callback_query.message.text != "Доступные на взятие задачи. \nЧтобы получить больше информации, нажмите на задачу.":
                        await callback_query.message.edit_text(
                            'Доступные на взятие задачи. \nЧтобы получить больше информации, нажмите на задачу.')
                    await callback_query.message.edit_reply_markup(
                        reply_markup=await representative_handler.generate_inline_keyboard_for_tasks(state,
                                                                                                     int(data[1]),
                                                                                                     data[2]))
                else:
                    to_answer = 'Кнопка устарела, начните заного'
        elif command == "task_info":
            to_answer = ''
            keyboard = InlineKeyboardMarkup()
            if data[3] == "history":
                keyboard.insert(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} history'))
            elif data[3] == "current":
                keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} current'))
                keyboard.insert(
                    InlineKeyboardButton('Отказаться от выполнения', callback_data=f'refuse_task {data[1]} {data[2]}'))
            elif data[3] == "available":
                keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} available'))
                keyboard.insert(InlineKeyboardButton('Взять', callback_data=f'take_task {data[1]} {data[2]}'))
            await callback_query.message.edit_text(
                text=utils.generate_task_description(db_worker.get_task(int(data[1]))), parse_mode="html")
            await callback_query.message.edit_reply_markup(reply_markup=keyboard)
        elif command == "refuse_task":
            to_answer = 'Подтвердите отказ от выполнения'
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} current'))
            keyboard.insert(InlineKeyboardButton('Отказаться от выполнения!',
                                                 callback_data=f'refuse_task_sure {data[1]} {data[2]}'))
            await callback_query.message.edit_reply_markup(reply_markup=keyboard)
        elif command == "refuse_task_sure":
            task = db_worker.get_task(int(data[1]))
            task.status = "awaiting_specialist"
            task.specialist = None
            # TODO уведомить как-то представителя 
            db_worker.Session.commit()
            tasks = db_worker.get_tasks_for_user(db_user, ['awaiting_confirmation', 'awaiting_specialist', 'in_work'])
            async with state.proxy() as state_data:
                state_data['tasks_current'] = tasks
            to_answer = 'Вы успешно отказались от задания!'
            await callback_query.message.edit_text(
                'Текущие задачи, которые Вы сейчас выполняете. \nЧтобы получить больше информации и редактировать, нажмите на задачу.')
            await callback_query.message.edit_reply_markup(
                reply_markup=await representative_handler.generate_inline_keyboard_for_tasks(state, int(data[2]),
                                                                                             'current'))
        elif command == "take_task":
            to_answer = 'Подтвердите взятие задачи'
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} current'))
            keyboard.insert(InlineKeyboardButton('Взять!', callback_data=f'take_task_sure {data[1]} {data[2]}'))
            await callback_query.message.edit_reply_markup(reply_markup=keyboard)
        elif command == "take_task_sure":
            db_user = db_worker.get_user(callback_query.from_user.id)
            task = db_worker.get_task(int(data[1]))
            task.status = "in_work"
            task.specialist = db_user.specialist
            # TODO уведомить как-то представителя 
            db_worker.Session.commit()
            tasks = db_worker.get_opened_tasks([sphere.spheres for sphere in db_user.specialist.spheres])
            async with state.proxy() as state_data:
                state_data['tasks_available'] = tasks
            to_answer = 'Вы успешно взяли задание'
            await callback_query.message.edit_text(
                'Доступные на взятие задачи. \nЧтобы получить больше информации, нажмите на задачу.')
            await callback_query.message.edit_reply_markup(
                reply_markup=await representative_handler.generate_inline_keyboard_for_tasks(state, int(data[2]),
                                                                                             'available'))
    elif db_user.status == "moderator":
        if command == "cp_tasks":
            async with state.proxy() as state_data:
                if f'tasks_{data[2]}' in state_data:
                    to_answer = ''
                    if data[
                        2] == 'unchecked' and callback_query.message.text != "Задачи, требующие модерацию. \nЧтобы получить больше информации и редактировать, нажмите на задачу.":
                        await callback_query.message.edit_text(
                            'Задачи, требующие модерацию. \nЧтобы получить больше информации и редактировать, нажмите на задачу.')
                    await callback_query.message.edit_reply_markup(
                        reply_markup=await representative_handler.generate_inline_keyboard_for_tasks(state,
                                                                                                     int(data[1]),
                                                                                                     data[2]))
                else:
                    to_answer = 'Кнопка устарела, начните заного'
        elif command == "task_info":
            to_answer = ''
            keyboard = InlineKeyboardMarkup()
            if data[3] == "unchecked":
                keyboard.add(InlineKeyboardButton('Назад', callback_data=f'cp_tasks {data[2]} available'))
                keyboard.insert(
                    InlineKeyboardButton('Отметить как подтверждённое', callback_data=f'confirm {data[1]} {data[2]}'))
            await callback_query.message.edit_text(
                text=utils.generate_task_description(db_worker.get_task(int(data[1]))), parse_mode="html")
            await callback_query.message.edit_reply_markup(reply_markup=keyboard)
        elif command == "confirm":
            db_user = db_worker.get_user(callback_query.from_user.id)
            task = db_worker.get_task(int(data[1]))
            task.status = "awaiting_specialist"
            # task.specialist = db_user.specialist
            # TODO уведомить специалистов
            db_worker.Session.commit()
            tasks = db_worker.get_unchecked_taskes()
            async with state.proxy() as state_data:
                state_data['tasks_unchecked'] = tasks
            to_answer = 'Вы отметили задание, как прошедшее модерацию'
            await callback_query.message.edit_text(
                'Задачи, требующие модерацию. \nЧтобы получить больше информации и редактировать, нажмите на задачу.')
            await callback_query.message.edit_reply_markup(
                reply_markup=await moderator_handler.generate_inline_keyboard_for_tasks(state, int(data[2]),
                                                                                        'unchecked'))

    await callback_query.answer(to_answer)
    if to_answer == "Ошибка, начните заного":
        logging.warning(f"Необработанный колбек \"{callback_query.data}\", состояние: {await state.get_state()}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
