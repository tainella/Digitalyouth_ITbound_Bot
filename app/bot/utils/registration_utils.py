from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_role_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('IT-специалист', callback_data='wish_specialist'))
    keyboard.add(InlineKeyboardButton('Модератор', callback_data='wish_moderator'))
    keyboard.add(InlineKeyboardButton('Представитель АНО «Цифровая молодёжь»', callback_data='wish_representative'))
    keyboard.add(InlineKeyboardButton('Назад', callback_data='back'))
    keyboard.insert(InlineKeyboardButton('Отмена', callback_data='cancel'))
    return keyboard
