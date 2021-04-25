from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

import db_worker

def generate_reply_keyboard_for_tasks_start():
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('Отмена', callback_data='cancel'))
    return keyboard

def generate_reply_keyboard_for_tasks():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Назад', callback_data='back'))
    keyboard.insert(InlineKeyboardButton('Отмена', callback_data='cancel'))
    return keyboard

def generate_reply_keyboard_for_tasks_done():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Назад', callback_data='back'))
    keyboard.insert(InlineKeyboardButton('Отмена', callback_data='cancel'))
    keyboard.insert(InlineKeyboardButton('Подтверждаю', callback_data='done'))
    return keyboard

def get_all_interests():
    # TODO получать список из бд
    return db_worker.get_all_interests()
    # return ["Дизайн", "Разработка ботов", "Вёрстка сайтов", "CRM", "Базы данных", "Аналитика", 'Машинное обучение'] 

# ☑️ ☐
async def generate_reply_keyboard_for_tasks_spheres(state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    even = True
    async with state.proxy() as data:
        spheres = data['spheres']
        for key in spheres:
            checked = "☑️ " if spheres[key] else '☐ ' # TODO поискать другие эмодзи
            if even:
                keyboard.add(InlineKeyboardButton(checked + key, callback_data=key))
            else:
                keyboard.insert(InlineKeyboardButton(checked + key, callback_data=key))
            even = not even 
    keyboard.add(InlineKeyboardButton('Назад', callback_data='back'))
    keyboard.insert(InlineKeyboardButton('Отмена', callback_data='cancel'))
    keyboard.insert(InlineKeyboardButton('Подтвердить', callback_data='done'))
    return keyboard