# -*- coding: utf-8 -*-

from pathlib import Path

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram import types
from sqlalchemy.orm.session import Session

from ..db.models import User


# Из res создаём словарь строк для UI
def res_(filename: str):
    return open(filename, 'r').read()


res_dict = {}
for file in Path("app/res").iterdir():
    res_dict[file.stem] = res_(str(file))


def generate_task_description(task) -> str:
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
    spheres = [sphere.spheres.name for sphere in task.spheres]
    to_return = res_dict['task_info'].format(task.name,
                                             task.description,
                                             ', '.join(spheres),
                                             status_str,
                                             task.representative.user.real_fullname,
                                             specialist_str,
                                             task.time_of_creation)
    return to_return


async def get_or_create_user(session: Session, message: types.Message) -> User:
    """
    :param session: Сессия sqlalchemy
    :param message: Сообщение от юзера
    :rtype: Юзер из Базы данных подключенные к сессии из аргументов
    """
    user = User.get(session, telegram_id=message.from_user.id)
    if not user:
        user = User(message.from_user.id, message.from_user.username, message.from_user.full_name)
        session.add(user)

    return user
