# -*- coding: utf-8 -*-

from pathlib import Path

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

import db_worker


# Из res создаём словарь строк для UI
def res_(filename: str):
    return open(filename, 'r').read()
res_dict = {}
for file in Path("res").iterdir():
    res_dict[file.stem] = res_(file)

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
    specialist_str = task.specialist.real_fullname if task.specialist is not None else "Не назначен"

    to_return = res_dict['task_info'].format(task.name,
        task.description,
        ', '.join(task.spheres),
        status_str,
        task.representative.user.real_fullname,
        specialist_str,
        task.time_of_creation)
    return to_return