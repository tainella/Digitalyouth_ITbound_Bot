
from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import res_dict
import db_worker

async def send_profile_specialist(db_user, message: types.Message, state: FSMContext):
    to_send = res_dict['profile_specialist'].format(db_user.real_fullname, db_user.phone, ', '.join(db_worker.get_spesialist_spheres(db_user.telegram_id)),
                        db_user.specialist.subsribed, None, None)

    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('Редактировать', callback_data='edit_profile'))
    await message.answer(to_send, parse_mode='html', reply_markup=keyboard)