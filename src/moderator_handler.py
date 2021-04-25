from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from utils import res_dict
import db_worker

async def generate_inline_keyboard_for_tasks(state: FSMContext, page_n:int, type_:str):
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

async def send_unchecked_taskes(db_user, unchecked_taskes, message: types.Message, state: FSMContext):
    async with state.proxy() as state_data:
        state_data['tasks_unchecked'] = unchecked_taskes
    await message.answer('Задачи, требующие модерацию. \nЧтобы получить больше информации и редактировать, нажмите на задачу.', parse_mode='html', reply_markup=await generate_inline_keyboard_for_tasks(state, 0, 'unchecked'))

	
	
