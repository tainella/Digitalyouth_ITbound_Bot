from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlalchemy.orm.session import Session

from .utils import res_dict
from ..db.models import Task, User


async def generate_inline_keyboard_for_tasks(state: FSMContext, page_n: int, type_: str):
    async with state.proxy() as state_data:
        tasks_list = state_data[f'tasks_{type_}']
    if page_n * 9 > len(tasks_list):
        return False
    else:
        reply_markup = types.InlineKeyboardMarkup()
        for index, task in enumerate(tasks_list[page_n * 9:(page_n + 1) * 9]):
            callback_data_to_input = f"task_info {task.id} {page_n} {type_}"
            reply_markup.add(types.InlineKeyboardButton(f"{page_n * 9 + (index + 1)}. {task.name}"[:60],
                                                        callback_data=callback_data_to_input))
        reply_markup.row()
        # cp_history - change page in history
        if page_n != 0:
            reply_markup.insert(types.InlineKeyboardButton("<<", callback_data=f'cp_tasks {page_n - 1} {type_}'))
        if (page_n + 1) * 9 < len(tasks_list):
            reply_markup.insert(types.InlineKeyboardButton(">>", callback_data=f'cp_tasks {page_n + 1} {type_}'))
        return reply_markup


async def send_unchecked_tasks(session: Session, message: types.Message, state: FSMContext):
    unchecked_tasks = session.query(Task).filter_by(status='awaiting_confirmation').all()

    async with state.proxy() as state_data:
        state_data['tasks_unchecked'] = unchecked_tasks
    await message.answer('Задачи, требующие модерацию. \nЧтобы получить больше информации и редактировать, нажмите на '
                         'задачу.', parse_mode='html',
                         reply_markup=await generate_inline_keyboard_for_tasks(state, 0, 'unchecked'))


async def send_profile(db_user, message: types.Message):
    to_send = res_dict['profile_moderator'].format(db_user.real_fullname, db_user.phone)
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('Редактировать', callback_data='edit_profile'))
    await message.answer(to_send, parse_mode='html', reply_markup=keyboard)
