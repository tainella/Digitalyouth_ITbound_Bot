
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

async def send_profile(db_user, message: types.Message, state: FSMContext):
    to_send = res_dict['profile_specialist'].format(db_user.real_fullname, db_user.phone, ', '.join(db_worker.get_spesialist_spheres(db_user)),
                        "Подписан" if db_user.specialist.subsribed else "Не подписан", None, None)

    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('Редактировать', callback_data='edit_profile'))
    await message.answer(to_send, parse_mode='html', reply_markup=keyboard)