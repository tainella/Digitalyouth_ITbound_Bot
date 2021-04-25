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


def generate_inline_keyboard_for_registration_start():
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('Отмена', callback_data='cancel'))
    return keyboard

def generate_role_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('IT-специалист', callback_data='wish_specialist'))
    keyboard.insert(InlineKeyboardButton('Модератор', callback_data='wish_moderator'))
    keyboard.insert(InlineKeyboardButton('Представитель АНО «Цифровая молодёжь»', callback_data='wish_representative'))
    keyboard.insert(InlineKeyboardButton('Отмена', callback_data='cancel'))
    return keyboard
