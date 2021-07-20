from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from ...db.models import User
from ...db.utils import get_tasks_for_user
from ..utils.general_utils import res_dict, generate_inline_keyboard_for_tasks


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


# ☑️ ☐
async def generate_reply_keyboard_for_tasks_spheres(state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    even = True
    async with state.proxy() as data:
        spheres = data['spheres']
        for key, sphere in spheres.items():
            checked = "☑️ " if sphere else '☐ '  # TODO поискать другие эмодзи
            if even:
                keyboard.add(InlineKeyboardButton(checked + key, callback_data=key))
            else:
                keyboard.insert(InlineKeyboardButton(checked + key, callback_data=key))
            even = not even
    keyboard.add(InlineKeyboardButton('Назад', callback_data='back'))
    keyboard.insert(InlineKeyboardButton('Отмена', callback_data='cancel'))
    keyboard.insert(InlineKeyboardButton('Подтвердить', callback_data='done'))
    return keyboard


async def send_profile(db_user: User, message: types.Message):
    to_send = res_dict['profile_representative'].format(db_user.real_fullname, db_user.phone_n,
                                                        len(get_tasks_for_user(db_user, (
                                                            'awaiting_confirmation', 'awaiting_specialist',
                                                            'in_work'))),
                                                        len(get_tasks_for_user(db_user, (
                                                            'closed_with_success', 'canceled_by_represented',
                                                            'closed_by_other_reason'))))
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('Редактировать', callback_data='edit_profile'))
    await message.answer(to_send, parse_mode='html', reply_markup=keyboard)


# async def generate_inline_keyboard_for_tasks(state: FSMContext, page_n: int, type_: str):
#     async with state.proxy() as state_data:
#         tasks_list = state_data[f'tasks_{type_}']
#     if page_n * 9 > len(tasks_list):
#         return False
#     else:
#         reply_markup = types.InlineKeyboardMarkup()
#         for index, task in enumerate(tasks_list[page_n * 9:(page_n + 1) * 9]):
#             callback_data_to_input = f"task_info {task.id} {page_n} {type_}"
#             reply_markup.add(types.InlineKeyboardButton(f"{page_n * 9 + (index + 1)}. {task.name}"[:60],
#                                                         callback_data=callback_data_to_input))
#         reply_markup.row()
#         # cp_history - change page in history
#         if page_n != 0:
#             reply_markup.insert(types.InlineKeyboardButton("<<", callback_data=f'cp_tasks {page_n - 1} {type_}'))
#         if (page_n + 1) * 9 < len(tasks_list):
#             reply_markup.insert(types.InlineKeyboardButton(">>", callback_data=f'cp_tasks {page_n + 1} {type_}'))
#         return reply_markup


async def tasks_history(db_user: User, message: types.Message, state: FSMContext):
    tasks = get_tasks_for_user(db_user, ('closed_with_success', 'canceled_by_represented', 'closed_by_other_reason'))
    if tasks:
        async with state.proxy() as state_data:
            state_data['tasks_history'] = tasks
        await message.answer('История задач, которые Вы добавляли. \nЧтобы получить больше информации, нажмите на '
                             'задачу.',
                             parse_mode='html',
                             reply_markup=await generate_inline_keyboard_for_tasks(state, 0, 'history'))
    else:
        await message.answer('На данный момент вы не добавили ни одной задачи', )


async def tasks_current(db_user: User, message: types.Message, state: FSMContext):
    tasks = get_tasks_for_user(db_user, ('awaiting_confirmation', 'awaiting_specialist', 'in_work'))
    if tasks:
        async with state.proxy() as state_data:
            state_data['tasks_current'] = tasks
        await message.answer(
            'Текущие задачи, которые Вы добавляли. \nЧтобы получить больше информации и редактировать, нажмите на '
            'задачу.',
            parse_mode='html', reply_markup=await generate_inline_keyboard_for_tasks(state, 0, 'current'))
    else:
        await message.answer('На данный момент вы не добавляли какие-либо задачи, чтобы получить задание, зайдите в '
                             'меню "Список доступных задач"')
