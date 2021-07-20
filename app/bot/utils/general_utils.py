# -*- coding: utf-8 -*-
from typing import List, Union
from pathlib import Path

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram import types
from sqlalchemy.orm.session import Session

from ...db.models import User, Task, Sphere, SphereToTask


# Из res создаём словарь строк для UI
def res_(filename: str):
    return open(filename, 'r').read()


res_dict = {}
for file in Path("app/res").iterdir():
    res_dict[file.stem] = res_(str(file))


def generate_task_description(task: Task) -> str:
    status_str = ''
    if task.status == "awaiting_confirmation":
        status_str = "Ожидает подтверждения модерацией"
    elif task.status == "awaiting_specialist":
        status_str = "Ожидает взятия исполнителем"
    elif task.status == "in_work":
        status_str = "Выполняется"
    elif task.status == "closed_with_success":
        status_str = "Выполнен удовлетворительно"
    elif task.status == "canceled_by_represented":
        status_str = "Закрыт заказчиком"
    elif task.status == "closed_by_other_reason":
        status_str = "Закрыт"
    specialist_str = task.specialist.user.real_fullname if task.specialist is not None else "Не назначен"
    spheres = [association.sphere.name for association in task.spheres]
    to_return = res_dict['task_info'].format(task.name,
                                             task.description,
                                             ', '.join(spheres),
                                             status_str,
                                             task.representative.user.real_fullname,
                                             specialist_str,
                                             task.time_of_creation)
    return to_return


async def get_or_create_user(session: Session, update: Union[types.Message, types.CallbackQuery]) -> User:
    """
    :param session: Сессия sqlalchemy
    :param update: Сообщение от юзера или callbackquery
    :rtype: Юзер из Базы данных подключенные к сессии из аргументов
    """
    user = User.get(session, telegram_id=update.from_user.id)
    if not user:
        user = User(update.from_user.id, update.from_user.username, update.from_user.full_name)
        session.add(user)

    return user


async def generate_inline_keyboard_for_tasks(state: FSMContext, page_n: int, type_: str):
    async with state.proxy() as state_data:
        tasks_list: List[Task] = state_data[f'tasks_{type_}']
    if page_n * 9 > len(tasks_list):
        return False
    else:
        reply_markup = types.InlineKeyboardMarkup()
        for index, task in enumerate(tasks_list[page_n * 9:(page_n + 1) * 9]):
            callback_data_to_input = f"task_info {task.id_} {page_n} {type_}"
            reply_markup.add(types.InlineKeyboardButton(f"{page_n * 9 + (index + 1)}. {task.name}"[:60],
                                                        callback_data=callback_data_to_input))
        reply_markup.row()
        # cp_history - change page in history
        if page_n != 0:
            reply_markup.insert(types.InlineKeyboardButton("<<", callback_data=f'cp_tasks {page_n - 1} {type_}'))
        if (page_n + 1) * 9 < len(tasks_list):
            reply_markup.insert(types.InlineKeyboardButton(">>", callback_data=f'cp_tasks {page_n + 1} {type_}'))
        return reply_markup


async def add_task(session: Session, callback_query: types.CallbackQuery, name: str, description: str,
                   spheres: List[str]) -> Task:
    db_user = User.get(session, telegram_id=callback_query.from_user.id)

    spheres_db = []
    for sphere_name in spheres:
        sphere_db = session.query(Sphere).filter_by(name=sphere_name).first()
        if sphere_db is None or not sphere_db.status:
            raise Exception(f'Сфера "{sphere_name}" не существует')
        else:
            spheres_db.append(sphere_db)

    new_task = Task(name, db_user.representative, description)
    new_task.status = 'awaiting_confirmation'
    for sphere in spheres_db:
        association = SphereToTask(sphere, new_task)
        session.add(association)
        session.commit()
    session.add(new_task)
    session.commit()
    return new_task


def generate_inline_keyboard_back_cancel():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Назад', callback_data='back'))
    keyboard.insert(InlineKeyboardButton('Отмена', callback_data='cancel'))
    return keyboard


def generate_inline_keyboard_cancel():
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('Отмена', callback_data='cancel'))
    return keyboard
